import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.models.recruiter_enums import DuplicateResolution
from app.schemas.upload_batch import DuplicateResolutionInput, RetryBatchInput, UploadBatchResponse
from app.services.upload_batch_service import (
    create_upload_batch,
    get_upload_batch,
    process_upload_batch,
    queue_retry,
    resolve_duplicate,
)


router = APIRouter()


def _not_found(error: LookupError) -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(error)})


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
    db: AsyncSession = Depends(get_db),
):
    payload = []
    for index, file in enumerate(files):
        content = await file.read()
        client_id = f"{index}:{file.filename}:{len(content)}"
        payload.append((client_id, file.filename or "resume.pdf", content, file.content_type or "application/pdf"))
    try:
        batch = await create_upload_batch(db, job_id, payload, criteria_set_id)
    except LookupError as error:
        raise _not_found(error) from error
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
    db: AsyncSession = Depends(get_db),
):
    del idempotency_key  # Persistence-level idempotency is introduced with shared bulk actions.
    try:
        selected = await queue_retry(db, batch_id, payload.item_ids if payload.scope == "SELECTED" else None)
        await db.commit()
        batch = await get_upload_batch(db, batch_id)
    except LookupError as error:
        raise _not_found(error) from error
    if selected:
        background_tasks.add_task(process_upload_batch, batch_id, selected)
    return batch


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
