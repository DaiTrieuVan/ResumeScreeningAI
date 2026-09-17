# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import asyncio
import hashlib
import json

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.models.recruiter_enums import DuplicateResolution
from app.schemas.final_release import ManualRecoveryRequest
from app.schemas.upload_batch import DuplicateResolutionInput, RetryBatchInput, UploadBatchResponse
from app.services.idempotency_service import IdempotencyConflict, claim_request, complete_request
from app.services.audit_service import add_audit_event
from app.services.upload_batch_service import (
    create_upload_batch,
    get_upload_batch,
    process_upload_batch,
    queue_manual_recovery,
    queue_retry,
    resolve_duplicate,
)
from app.services.upload_recovery_service import reconcile_interrupted_items


router = APIRouter()


def _not_found(error: LookupError) -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(error)})


def _snapshot(batch) -> dict:
    return UploadBatchResponse.model_validate(batch).model_dump(mode="json")


def _conflict(error: Exception) -> HTTPException:
    return HTTPException(status_code=409, detail={"code": "CONFLICT", "message": str(error)})


@router.post(
    "/jobs/{job_id}/upload-batches",
    response_model=UploadBatchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_batch(
    job_id: str,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    criteria_set_id: str | None = Form(None),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_actor_id: str = Header("system"),
    db: AsyncSession = Depends(get_db),
):
    payload = []
    for index, file in enumerate(files):
        content = await file.read()
        client_id = f"{index}:{file.filename}:{len(content)}"
        payload.append((client_id, file.filename or "resume.pdf", content, file.content_type or "application/pdf"))
    fingerprint_payload = {
        "job_id": job_id,
        "criteria_set_id": criteria_set_id,
        "files": [{"client_id": item[0], "sha256": hashlib.sha256(item[2]).hexdigest()} for item in payload],
    }
    try:
        claim = await claim_request(db, actor_id=x_actor_id, operation="CREATE_BATCH", idempotency_key=idempotency_key, payload=fingerprint_payload)
        if claim.replayed:
            if claim.record.status == "COMPLETED":
                return claim.record.response_body
            raise IdempotencyConflict("Yêu cầu tạo lô này đang được xử lý.")
        batch = await create_upload_batch(db, job_id, payload, criteria_set_id)
        response_body = _snapshot(batch)
        await complete_request(db, claim.record, resource_id=batch.id, response_status=202, response_body=response_body)
    except LookupError as error:
        raise _not_found(error) from error
    except IdempotencyConflict as error:
        raise _conflict(error) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail={"code": "INVALID_BATCH", "message": str(error)}) from error
    await db.commit()
    batch = await get_upload_batch(db, batch.id)
    background_tasks.add_task(process_upload_batch, batch.id)
    return batch


@router.get("/upload-batches/{batch_id}", response_model=UploadBatchResponse)
async def read_batch(batch_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_upload_batch(db, batch_id)
    except LookupError as error:
        raise _not_found(error) from error


@router.get("/upload-batches/{batch_id}/events")
async def batch_events(batch_id: str):
    async def stream():
        previous = None
        for _ in range(120):
            async with AsyncSessionLocal() as db:
                try:
                    batch = await get_upload_batch(db, batch_id)
                except LookupError:
                    yield f"data: {json.dumps({'code': 'NOT_FOUND'})}\n\n"
                    return
                snapshot = UploadBatchResponse.model_validate(batch).model_dump(mode="json")
            serialized = json.dumps(snapshot, ensure_ascii=False)
            if serialized != previous:
                yield f"data: {serialized}\n\n"
                previous = serialized
            if snapshot["status"] in {"COMPLETED", "COMPLETED_WITH_ERRORS", "CANCELLED"}:
                return
            await asyncio.sleep(1)
    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/upload-batches/{batch_id}/retry", response_model=UploadBatchResponse, status_code=202)
async def retry_batch(
    batch_id: str,
    payload: RetryBatchInput,
    background_tasks: BackgroundTasks,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_actor_id: str = Header("system"),
    db: AsyncSession = Depends(get_db),
):
    try:
        request_payload = {"batch_id": batch_id, **payload.model_dump()}
        claim = await claim_request(db, actor_id=x_actor_id, operation="RETRY_BATCH", idempotency_key=idempotency_key, payload=request_payload)
        if claim.replayed:
            if claim.record.status == "COMPLETED":
                return claim.record.response_body
            raise IdempotencyConflict("Yêu cầu thử lại này đang được xử lý.")
        selected = await queue_retry(db, batch_id, payload.item_ids if payload.scope == "SELECTED" else None)
        batch = await get_upload_batch(db, batch_id)
        response_body = _snapshot(batch)
        await complete_request(db, claim.record, resource_id=batch.id, response_status=202, response_body=response_body)
        await db.commit()
    except LookupError as error:
        raise _not_found(error) from error
    except IdempotencyConflict as error:
        raise _conflict(error) from error
    if selected:
        background_tasks.add_task(process_upload_batch, batch_id, selected)
    return batch


@router.post("/upload-batches/{batch_id}/recover", response_model=UploadBatchResponse, status_code=202)
async def recover_batch(
    batch_id: str,
    background_tasks: BackgroundTasks,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_actor_id: str = Header("system"),
    db: AsyncSession = Depends(get_db),
):
    try:
        claim = await claim_request(db, actor_id=x_actor_id, operation="RECOVER_BATCH", idempotency_key=idempotency_key, payload={"batch_id": batch_id})
        if claim.replayed:
            if claim.record.status == "COMPLETED":
                return claim.record.response_body
            raise IdempotencyConflict("Yêu cầu phục hồi này đang được xử lý.")
        await get_upload_batch(db, batch_id)
        resumed = await reconcile_interrupted_items(db, batch_id)
        from app.services.upload_batch_service import recalculate_batch
        await recalculate_batch(db, batch_id)
        batch = await get_upload_batch(db, batch_id)
        response_body = _snapshot(batch)
        await complete_request(db, claim.record, resource_id=batch_id, response_status=202, response_body=response_body)
        await db.commit()
        selected = resumed.get(batch_id, [])
        if selected:
            background_tasks.add_task(process_upload_batch, batch_id, selected)
        return batch
    except LookupError as error:
        raise _not_found(error) from error
    except IdempotencyConflict as error:
        raise _conflict(error) from error


@router.post("/upload-items/{item_id}/manual-recovery", response_model=UploadBatchResponse, status_code=202)
async def manual_recovery(
    item_id: str,
    payload: ManualRecoveryRequest,
    background_tasks: BackgroundTasks,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_actor_id: str = Header("system"),
    db: AsyncSession = Depends(get_db),
):
    try:
        claim = await claim_request(
            db, actor_id=x_actor_id, operation="MANUAL_RECOVERY", idempotency_key=idempotency_key,
            payload={"item_id": item_id, **payload.model_dump()},
        )
        if claim.replayed:
            if claim.record.status == "COMPLETED":
                return claim.record.response_body
            raise IdempotencyConflict("Yêu cầu xác minh này đang được xử lý.")
        item = await queue_manual_recovery(db, item_id, payload.verified_text)
        add_audit_event(
            db,
            actor_id=x_actor_id,
            action="MANUAL_RECOVERY_VERIFIED",
            resource_type="UploadItem",
            resource_id=item.id,
            resource_version=item.version,
            metadata={"verified_text": payload.verified_text, "reason": payload.reason, "extraction_method": "MANUAL"},
        )
        batch = await get_upload_batch(db, item.batch_id)
        response_body = _snapshot(batch)
        await complete_request(db, claim.record, resource_id=item.id, response_status=202, response_body=response_body)
        await db.commit()
        background_tasks.add_task(process_upload_batch, batch.id, [item.id])
        return batch
    except LookupError as error:
        raise _not_found(error) from error
    except (RuntimeError, IdempotencyConflict) as error:
        raise _conflict(error) from error


@router.post("/upload-items/{item_id}/duplicate-resolution", response_model=UploadBatchResponse)
async def decide_duplicate(
    item_id: str,
    payload: DuplicateResolutionInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if payload.resolution == DuplicateResolution.NEEDS_REVIEW:
        raise HTTPException(status_code=422, detail={"code": "INVALID_RESOLUTION", "message": "Hãy chọn cách xử lý CV trùng."})
    try:
        item, should_process = await resolve_duplicate(db, item_id, payload.resolution.value)
        await db.commit()
        batch = await get_upload_batch(db, item.batch_id)
    except LookupError as error:
        raise _not_found(error) from error
    if should_process:
        background_tasks.add_task(process_upload_batch, batch.id, [item.id])
    return batch
