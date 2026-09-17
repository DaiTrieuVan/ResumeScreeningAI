# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import asyncio
import hashlib
import os
import re
import uuid
from datetime import datetime

import aiofiles
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.models.recruiter_enums import (
    DuplicateMatchType,
    DuplicateResolution,
    UploadBatchStatus,
    UploadItemStatus,
)
from app.models.upload_batch import DuplicateMatch, UploadBatch, UploadItem
from app.models.final_release import ResumePage
from app.services.pdf_parser import build_page_records, extract_resume_metadata, extract_text_with_pages
from app.services.upload_recovery_service import acquire_processing_lease, release_processing_lease


MAX_BATCH_FILES = settings.MAX_BATCH_FILES
MAX_FILE_BYTES = settings.MAX_UPLOAD_FILE_BYTES
PROCESSING_STATUSES = {
    UploadItemStatus.VALIDATING.value,
    UploadItemStatus.PARSING.value,
    UploadItemStatus.READY.value,
    UploadItemStatus.EVALUATING.value,
}

ALLOWED_TRANSITIONS = {
    UploadItemStatus.QUEUED.value: {UploadItemStatus.VALIDATING.value, UploadItemStatus.CANCELLED.value},
    UploadItemStatus.VALIDATING.value: {UploadItemStatus.PARSING.value, UploadItemStatus.FAILED.value},
    UploadItemStatus.PARSING.value: {
        UploadItemStatus.NEEDS_OCR.value,
        UploadItemStatus.DEDUPE_REVIEW.value,
        UploadItemStatus.READY.value,
        UploadItemStatus.FAILED.value,
    },
    UploadItemStatus.READY.value: {UploadItemStatus.EVALUATING.value, UploadItemStatus.COMPLETED.value},
    UploadItemStatus.EVALUATING.value: {UploadItemStatus.COMPLETED.value, UploadItemStatus.FAILED.value},
    UploadItemStatus.FAILED.value: {UploadItemStatus.QUEUED.value},
    UploadItemStatus.NEEDS_OCR.value: {UploadItemStatus.QUEUED.value, UploadItemStatus.CANCELLED.value},
    UploadItemStatus.DEDUPE_REVIEW.value: {UploadItemStatus.QUEUED.value, UploadItemStatus.COMPLETED.value, UploadItemStatus.CANCELLED.value},
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def file_digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def content_digest(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip().casefold()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def contact_digest(email: str | None, phone: str | None) -> str | None:
    normalized_email = (email or "").strip().casefold()
    normalized_phone = re.sub(r"\D", "", phone or "")
    if not normalized_email and not normalized_phone:
        return None
    return hashlib.sha256(f"{normalized_email}|{normalized_phone}".encode("utf-8")).hexdigest()


async def get_upload_batch(db: AsyncSession, batch_id: str) -> UploadBatch:
    result = await db.execute(
        select(UploadBatch)
        .options(selectinload(UploadBatch.items).selectinload(UploadItem.duplicate_matches))
        .where(UploadBatch.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise LookupError(f"Không tìm thấy lô CV {batch_id}.")
    return batch


async def create_upload_batch(
    db: AsyncSession,
    job_id: str,
    files: list[tuple[str, str, bytes, str]],
    criteria_set_id: str | None = None,
    actor_id: str = "system",
) -> UploadBatch:
    if not files or len(files) > MAX_BATCH_FILES:
        raise ValueError(f"Mỗi lô cần từ 1 đến {MAX_BATCH_FILES} CV.")
    job = await db.get(JobPosting, job_id)
    if not job:
        raise LookupError(f"Không tìm thấy vị trí tuyển dụng {job_id}.")
    criteria_set_id = criteria_set_id or job.active_criteria_set_id

    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    batch = UploadBatch(
        job_id=job_id,
        criteria_set_id=criteria_set_id,
        created_by=actor_id,
        total_count=len(files),
        queued_count=len(files),
        items=[],
    )
    db.add(batch)
    await db.flush()

    seen_hashes: dict[str, UploadItem] = {}
    for client_file_id, original_name, content, mime_type in files:
        safe_name = os.path.basename(original_name or "resume.pdf")
        storage_name = f"batch_{uuid.uuid4().hex}_{safe_name}"
        storage_path = os.path.join(settings.STORAGE_DIR, storage_name)
        digest = file_digest(content)
        item = UploadItem(
            id=str(uuid.uuid4()),
            batch_id=batch.id,
            client_file_id=client_file_id,
            original_file_name=safe_name,
            mime_type=mime_type or "application/pdf",
            byte_size=len(content),
            storage_key=storage_path,
            file_sha256=digest,
            duplicate_matches=[],
        )
        if len(content) > MAX_FILE_BYTES:
            item.status = UploadItemStatus.FAILED.value
            item.error_code = "FILE_TOO_LARGE"
            item.user_message = "Tệp vượt quá giới hạn 15 MB."
        elif not safe_name.lower().endswith(".pdf") or not content.startswith(b"%PDF"):
            item.status = UploadItemStatus.FAILED.value
            item.error_code = "INVALID_PDF"
            item.user_message = "Tệp không phải PDF hợp lệ."
        else:
            async with aiofiles.open(storage_path, "wb") as output:
                await output.write(content)
            if digest in seen_hashes:
                item.status = UploadItemStatus.DEDUPE_REVIEW.value
                item.user_message = "Tệp này trùng hoàn toàn với một CV khác trong cùng lô."
                item.duplicate_matches.append(DuplicateMatch(
                    matched_upload_item_id=seen_hashes[digest].id,
                    match_type=DuplicateMatchType.EXACT_FILE.value,
                    confidence=1.0,
                ))
            else:
                seen_hashes[digest] = item
        batch.items.append(item)

    await db.flush()
    await recalculate_batch(db, batch.id)
    return await get_upload_batch(db, batch.id)


async def _find_duplicate(
    db: AsyncSession, item: UploadItem, job_id: str
) -> tuple[UploadItem, str, float] | None:
    conditions = [UploadItem.file_sha256 == item.file_sha256]
    if item.contact_fingerprint:
        conditions.append(UploadItem.contact_fingerprint == item.contact_fingerprint)
    if item.content_fingerprint:
        conditions.append(UploadItem.content_fingerprint == item.content_fingerprint)
    result = await db.execute(
        select(UploadItem)
        .join(UploadBatch, UploadBatch.id == UploadItem.batch_id)
        .where(
            UploadBatch.job_id == job_id,
            UploadItem.id != item.id,
            UploadItem.candidate_resume_id.is_not(None),
            or_(*conditions),
        )
        .order_by(UploadItem.created_at.asc())
        .limit(1)
    )
    matched = result.scalar_one_or_none()
    if not matched:
        return None
    if matched.file_sha256 == item.file_sha256:
        return matched, DuplicateMatchType.EXACT_FILE.value, 1.0
    if item.contact_fingerprint and matched.contact_fingerprint == item.contact_fingerprint:
        return matched, DuplicateMatchType.CONTACT.value, 0.95
    return matched, DuplicateMatchType.SIMILAR_CONTENT.value, 0.9


async def process_upload_item(item_id: str) -> None:
    async with AsyncSessionLocal() as db:
        item = await db.get(UploadItem, item_id)
        if not item or item.status != UploadItemStatus.QUEUED.value:
            return
        batch = await db.get(UploadBatch, item.batch_id)
        if not batch:
            return
        lease_token = await acquire_processing_lease(db, item)
        if not lease_token:
            await db.commit()
            return
        item.status = UploadItemStatus.VALIDATING.value
        item.error_code = item.user_message = item.technical_detail = None
        await db.commit()

        try:
            item.status = UploadItemStatus.PARSING.value
            await db.commit()
            if item.manual_text:
                raw_text, page_records = build_page_records([item.manual_text], extraction_method="MANUAL")
                item.extraction_method = "MANUAL"
            else:
                raw_text, page_records = await asyncio.to_thread(extract_text_with_pages, item.storage_key)
                item.extraction_method = "NATIVE"
            metadata = extract_resume_metadata(raw_text)
            item.content_fingerprint = content_digest(raw_text)
            item.contact_fingerprint = contact_digest(metadata.get("email"), metadata.get("phone"))

            keep_both = await db.scalar(
                select(DuplicateMatch.id).where(
                    DuplicateMatch.upload_item_id == item.id,
                    DuplicateMatch.resolution == DuplicateResolution.KEEP_BOTH.value,
                ).limit(1)
            )
            duplicate = None if keep_both else await _find_duplicate(db, item, batch.job_id)
            if duplicate:
                matched, match_type, confidence = duplicate
                existing_match = await db.scalar(
                    select(DuplicateMatch.id).where(
                        DuplicateMatch.upload_item_id == item.id,
                        DuplicateMatch.matched_upload_item_id == matched.id,
                        DuplicateMatch.match_type == match_type,
                    ).limit(1)
                )
                if not existing_match:
                    db.add(DuplicateMatch(
                        upload_item_id=item.id,
                        matched_upload_item_id=matched.id,
                        match_type=match_type,
                        confidence=confidence,
                    ))
                item.status = UploadItemStatus.DEDUPE_REVIEW.value
                item.user_message = "Phát hiện CV có khả năng trùng. Cần recruiter xác nhận."
            else:
                item.status = UploadItemStatus.READY.value
                resume = CandidateResume(
                    job_id=batch.job_id,
                    file_name=item.original_file_name,
                    file_path=item.storage_key or "",
                    file_size_bytes=item.byte_size,
                    raw_text=raw_text,
                    parsed_name=metadata.get("candidate_name"),
                    parsed_email=metadata.get("email"),
                    parsed_phone=metadata.get("phone"),
                    parse_status="SUCCESS",
                )
                db.add(resume)
                await db.flush()
                for page in page_records:
                    db.add(ResumePage(resume_id=resume.id, **page))
                item.candidate_resume_id = resume.id
                item.status = UploadItemStatus.COMPLETED.value
        except Exception as error:
            message = str(error)
            if "empty" in message.casefold() or "no readable" in message.casefold():
                item.status = UploadItemStatus.NEEDS_OCR.value
                item.error_code = "OCR_REQUIRED"
                item.user_message = "PDF không có lớp chữ; cần OCR hoặc kiểm tra thủ công."
            else:
                item.status = UploadItemStatus.FAILED.value
                item.error_code = "PARSE_FAILED"
                item.user_message = "Không thể đọc CV. Bạn có thể thử lại hoặc thay tệp khác."
            item.technical_detail = message[:2000]
            item.last_failure_at = datetime.utcnow()
        item.version += 1
        await release_processing_lease(db, item.id, lease_token)
        await db.commit()


async def recalculate_batch(db: AsyncSession, batch_id: str) -> UploadBatch:
    batch = await get_upload_batch(db, batch_id)
    statuses = [item.status for item in batch.items]
    batch.queued_count = statuses.count(UploadItemStatus.QUEUED.value)
    batch.processing_count = sum(status in PROCESSING_STATUSES for status in statuses)
    batch.success_count = statuses.count(UploadItemStatus.COMPLETED.value)
    batch.failed_count = statuses.count(UploadItemStatus.FAILED.value) + statuses.count(UploadItemStatus.NEEDS_OCR.value)
    batch.duplicate_count = statuses.count(UploadItemStatus.DEDUPE_REVIEW.value)
    batch.cancelled_count = statuses.count(UploadItemStatus.CANCELLED.value)

    if batch.queued_count or batch.processing_count:
        batch.status = UploadBatchStatus.PROCESSING.value
        batch.completed_at = None
    elif batch.failed_count or batch.duplicate_count:
        batch.status = UploadBatchStatus.COMPLETED_WITH_ERRORS.value
        batch.completed_at = datetime.utcnow()
    else:
        batch.status = UploadBatchStatus.COMPLETED.value
        batch.completed_at = datetime.utcnow()
    await db.flush()
    return batch


async def process_upload_batch(batch_id: str, item_ids: list[str] | None = None) -> None:
    async with AsyncSessionLocal() as db:
        batch = await get_upload_batch(db, batch_id)
        targets = [item.id for item in batch.items if item.status == UploadItemStatus.QUEUED.value]
        if item_ids is not None:
            targets = [item_id for item_id in targets if item_id in item_ids]
        batch.status = UploadBatchStatus.PROCESSING.value
        await db.commit()

    semaphore = asyncio.Semaphore(4)

    async def run_one(item_id: str):
        async with semaphore:
            await process_upload_item(item_id)

    await asyncio.gather(*(run_one(item_id) for item_id in targets), return_exceptions=True)
    async with AsyncSessionLocal() as db:
        await recalculate_batch(db, batch_id)
        await db.commit()


async def queue_retry(
    db: AsyncSession, batch_id: str, item_ids: list[str] | None = None
) -> list[str]:
    batch = await get_upload_batch(db, batch_id)
    retryable = {UploadItemStatus.FAILED.value, UploadItemStatus.NEEDS_OCR.value}
    selected = []
    for item in batch.items:
        if item.status in retryable and (not item_ids or item.id in item_ids):
            if item.attempt_count >= settings.UPLOAD_MAX_ATTEMPTS:
                item.error_code = "RETRY_LIMIT_REACHED"
                item.user_message = "Đã đạt giới hạn thử lại. Hãy kiểm tra hoặc thay tệp thủ công."
                continue
            item.status = UploadItemStatus.QUEUED.value
            item.version += 1
            selected.append(item.id)
    await recalculate_batch(db, batch_id)
    return selected


async def queue_manual_recovery(db: AsyncSession, item_id: str, verified_text: str) -> UploadItem:
    item = await db.get(UploadItem, item_id)
    if not item:
        raise LookupError("Không tìm thấy CV cần phục hồi.")
    if item.status not in {UploadItemStatus.NEEDS_OCR.value, UploadItemStatus.FAILED.value}:
        raise RuntimeError("Chỉ có thể nhập nội dung xác minh cho CV đang cần xử lý.")
    item.manual_text = verified_text.strip()
    item.extraction_method = "MANUAL"
    item.status = UploadItemStatus.QUEUED.value
    item.error_code = None
    item.user_message = "Đã nhận văn bản xác minh; CV sẵn sàng xử lý lại."
    item.version += 1
    await recalculate_batch(db, item.batch_id)
    return item


async def resolve_duplicate(
    db: AsyncSession, item_id: str, resolution: str, actor_id: str = "system"
) -> tuple[UploadItem, bool]:
    result = await db.execute(
        select(UploadItem)
        .options(selectinload(UploadItem.duplicate_matches))
        .where(UploadItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item or item.status != UploadItemStatus.DEDUPE_REVIEW.value:
        raise LookupError("Không tìm thấy mục trùng đang chờ xử lý.")
    match = item.duplicate_matches[0]
    match.resolution = resolution
    match.resolved_by = actor_id
    match.resolved_at = datetime.utcnow()
    should_process = False
    if resolution == DuplicateResolution.KEEP_BOTH.value:
        item.status = UploadItemStatus.QUEUED.value
        should_process = True
    elif resolution == DuplicateResolution.LINK_EXISTING.value:
        matched = await db.get(UploadItem, match.matched_upload_item_id)
        item.candidate_resume_id = matched.candidate_resume_id if matched else None
        item.status = UploadItemStatus.COMPLETED.value
    else:
        item.status = UploadItemStatus.CANCELLED.value
    item.version += 1
    await recalculate_batch(db, item.batch_id)
    return item, should_process
