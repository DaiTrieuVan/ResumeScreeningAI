# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.candidate_evaluation import CandidateApplication
from app.models.recruiter_enums import PipelineStage
from app.models.recruiter_productivity import BulkActionItem, BulkActionRequest, CandidateTag, CandidateTagAssignment, SavedView
from app.repositories.candidate_query_repository import query_candidates
from app.services.candidate_privacy_service import get_review_privacy_policy, mask_candidate_projection

router = APIRouter()


class SavedViewInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    columns: list[str] = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)
    sort: str = "score_desc"
    is_default: bool = False


class BulkActionInput(BaseModel):
    action: str
    application_ids: list[str] = Field(min_length=1, max_length=200)
    expected_versions: dict[str, int] = Field(default_factory=dict)
    value: str


def candidate_item(application, resume, evaluation):
    return {"application_id": application.id, "version": application.version, "candidate_name": resume.parsed_name or resume.file_name, "candidate_email": resume.parsed_email, "file_name": resume.file_name, "stage": application.pipeline_stage, "received_at": application.received_at, "score": evaluation.overall_score if evaluation else None, "mandatory_gate": evaluation.mandatory_gate if evaluation else "NEEDS_REVIEW", "skills": resume.extracted_skills or []}


def bulk_result(request):
    return {"id": request.id, "status": request.status, "total_count": request.total_count, "success_count": request.success_count, "failure_count": request.failure_count, "items": [{"application_id": item.application_id, "outcome": item.outcome, "error_code": item.error_code, "resulting_version": item.resulting_version} for item in request.items]}


@router.get("/jobs/{job_id}/candidates")
async def candidates(job_id: str, q: str | None = Query(None, max_length=200), stage: list[str] = Query(default=[]), mandatory_gate: str | None = None, min_score: float | None = Query(None, ge=0, le=100), skills: list[str] = Query(default=[]), sort: str = "score_desc", page: int = Query(1, ge=1), page_size: int = Query(25, ge=10, le=100), db: AsyncSession = Depends(get_db)):
    rows, total = await query_candidates(db, job_id, q=q, stages=stage, mandatory_gate=mandatory_gate, min_score=min_score, skills=skills, sort=sort, page=page, page_size=page_size)
    policy = await get_review_privacy_policy(db, job_id)
    items = [candidate_item(*row) for row in rows]
    if policy.mode == "BLIND":
        items = [mask_candidate_projection(item[0].id, candidate_item(*item)) for item in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size, "facets": {"filtered": total}, "privacy_mode": policy.mode}


@router.get("/jobs/{job_id}/saved-views")
async def list_saved_views(job_id: str, db: AsyncSession = Depends(get_db)):
    views = (await db.scalars(select(SavedView).where(SavedView.job_id == job_id))).all()
    return [{"id": view.id, "name": view.name, "columns": view.columns, "filters": view.filters, "sort": view.sort, "is_default": view.is_default} for view in views]


@router.post("/jobs/{job_id}/saved-views", status_code=201)
async def save_view(job_id: str, payload: SavedViewInput, db: AsyncSession = Depends(get_db)):
    view = SavedView(job_id=job_id, **payload.model_dump())
    db.add(view)
    await db.flush()
    return {"id": view.id, **payload.model_dump()}


@router.post("/jobs/{job_id}/bulk-actions", status_code=202)
async def bulk_action(job_id: str, payload: BulkActionInput, idempotency_key: str = Header(min_length=8, max_length=128), db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(BulkActionRequest).options(selectinload(BulkActionRequest.items)).where(BulkActionRequest.actor_id == "system", BulkActionRequest.idempotency_key == idempotency_key))
    if existing:
        return bulk_result(existing)
    if payload.action not in {"MOVE_STAGE", "ADD_TAG"}:
        raise HTTPException(422, detail={"code": "INVALID_ACTION", "message": "Hành động hàng loạt không được hỗ trợ."})
    if payload.action == "MOVE_STAGE" and payload.value not in {item.value for item in PipelineStage}:
        raise HTTPException(422, detail={"code": "INVALID_STAGE", "message": "Giai đoạn không hợp lệ."})
    request = BulkActionRequest(job_id=job_id, idempotency_key=idempotency_key, action=payload.action, payload={"value": payload.value}, total_count=len(payload.application_ids), items=[])
    db.add(request)
    tag = None
    if payload.action == "ADD_TAG":
        normalized = payload.value.strip().casefold()
        tag = await db.scalar(select(CandidateTag).where(CandidateTag.normalized_name == normalized))
        if not tag:
            tag = CandidateTag(name=payload.value.strip(), normalized_name=normalized)
            db.add(tag)
            await db.flush()
    for application_id in payload.application_ids:
        application = await db.get(CandidateApplication, application_id)
        expected = payload.expected_versions.get(application_id)
        if not application or application.job_id != job_id:
            item = BulkActionItem(application_id=application_id, expected_version=expected, outcome="FAILED", error_code="NOT_FOUND")
            request.failure_count += 1
        elif expected is not None and application.version != expected:
            item = BulkActionItem(application_id=application_id, expected_version=expected, outcome="FAILED", error_code="VERSION_CONFLICT", resulting_version=application.version)
            request.failure_count += 1
        else:
            if payload.action == "MOVE_STAGE":
                application.pipeline_stage = payload.value
                application.version += 1
            else:
                assignment = await db.scalar(select(CandidateTagAssignment).where(CandidateTagAssignment.application_id == application.id, CandidateTagAssignment.tag_id == tag.id))
                if not assignment:
                    db.add(CandidateTagAssignment(application_id=application.id, tag_id=tag.id))
            item = BulkActionItem(application_id=application_id, expected_version=expected, outcome="SUCCESS", resulting_version=application.version)
            request.success_count += 1
        request.items.append(item)
    request.status = "COMPLETED" if not request.failure_count else "COMPLETED_WITH_ERRORS"
    await db.flush()
    return bulk_result(request)
