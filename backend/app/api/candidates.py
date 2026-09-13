# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.candidate_detail import CandidateDetailResponse, EvaluationResponse
from app.services.evidence_service import load_candidate_detail
from app.services.candidate_privacy_service import anonymize_candidate, record_candidate_access, require_candidate_access


router = APIRouter()


@router.get("/applications/{application_id}", response_model=CandidateDetailResponse)
async def get_candidate_detail(application_id: str, x_actor_id: str = Header("system"), x_actor_role: str = Header("system"), db: AsyncSession = Depends(get_db)):
    try:
        require_candidate_access(x_actor_role)
    except PermissionError as error:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": str(error)}) from error
    try:
        application, resume, evaluation = await load_candidate_detail(db, application_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    record_candidate_access(db, application, x_actor_id, "VIEW_CANDIDATE_DETAIL")
    return CandidateDetailResponse(
        application_id=application.id,
        application_version=application.version,
        job_id=application.job_id,
        resume_id=resume.id,
        pipeline_stage=application.pipeline_stage,
        candidate_name=resume.parsed_name or resume.file_name,
        candidate_email=resume.parsed_email,
        candidate_phone=resume.parsed_phone,
        file_name=resume.file_name,
        extracted_skills=resume.extracted_skills or [],
        work_history=resume.work_history or [],
        education=resume.education or [],
        field_confidence={
            "name": 0.8 if resume.parsed_name else None,
            "email": 0.95 if resume.parsed_email else None,
            "phone": 0.9 if resume.parsed_phone else None,
        },
        evaluation=EvaluationResponse.model_validate(evaluation) if evaluation else None,
    )


@router.get("/applications/{application_id}/resume")
async def view_original_resume(application_id: str, x_actor_id: str = Header("system"), x_actor_role: str = Header("system"), db: AsyncSession = Depends(get_db)):
    try:
        require_candidate_access(x_actor_role)
    except PermissionError as error:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": str(error)}) from error
    try:
        application, resume, _ = await load_candidate_detail(db, application_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(error)}) from error

    storage_root = Path(settings.STORAGE_DIR).resolve()
    file_path = Path(resume.file_path).resolve()
    if not file_path.is_relative_to(storage_root) or not file_path.is_file():
        raise HTTPException(status_code=404, detail={"code": "RESUME_NOT_FOUND", "message": "Không tìm thấy CV gốc."})

    record_candidate_access(db, application, x_actor_id, "VIEW_ORIGINAL_RESUME")
    return FileResponse(file_path, media_type="application/pdf", filename=resume.file_name, content_disposition_type="inline")


@router.delete("/applications/{application_id}/personal-data", status_code=204)
async def delete_candidate_personal_data(application_id: str, x_actor_id: str = Header("system"), x_actor_role: str = Header("system"), db: AsyncSession = Depends(get_db)):
    try:
        require_candidate_access(x_actor_role)
        await anonymize_candidate(db, application_id, x_actor_id)
    except PermissionError as error:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": str(error)}) from error
    except LookupError as error:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": str(error)}) from error
