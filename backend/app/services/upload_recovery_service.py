# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import os
import socket
import uuid
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.final_release import ProcessingLease
from app.models.recruiter_enums import UploadItemStatus
from app.models.upload_batch import UploadItem


INTERRUPTED_STATUSES = {
    UploadItemStatus.VALIDATING.value,
    UploadItemStatus.PARSING.value,
    UploadItemStatus.READY.value,
    UploadItemStatus.EVALUATING.value,
}


def worker_id() -> str:
    return f"{socket.gethostname()}:{os.getpid()}"


async def acquire_processing_lease(db: AsyncSession, item: UploadItem) -> str | None:
    now = datetime.utcnow()
    current = await db.get(ProcessingLease, item.id)
    if current and current.expires_at > now:
        return None
    if item.attempt_count >= settings.UPLOAD_MAX_ATTEMPTS:
        item.status = UploadItemStatus.FAILED.value
        item.error_code = "RETRY_LIMIT_REACHED"
        item.user_message = "Đã đạt giới hạn thử lại. Hãy kiểm tra hoặc thay tệp thủ công."
        item.last_failure_at = now
        return None
    if current:
        await db.delete(current)
        await db.flush()
    token = uuid.uuid4().hex
    item.attempt_count += 1
    db.add(ProcessingLease(
        upload_item_id=item.id,
        owner_id=worker_id(),
        lease_token=token,
        acquired_at=now,
        heartbeat_at=now,
        expires_at=now + timedelta(seconds=settings.PROCESSING_LEASE_SECONDS),
        attempt=item.attempt_count,
    ))
    await db.flush()
    return token


async def release_processing_lease(db: AsyncSession, item_id: str, lease_token: str) -> bool:
    result = await db.execute(delete(ProcessingLease).where(
        ProcessingLease.upload_item_id == item_id,
        ProcessingLease.lease_token == lease_token,
    ))
    return bool(result.rowcount)


async def reconcile_interrupted_items(db: AsyncSession, batch_id: str | None = None) -> dict[str, list[str]]:
    now = datetime.utcnow()
    query = select(UploadItem).where(UploadItem.status.in_(INTERRUPTED_STATUSES))
    if batch_id:
        query = query.where(UploadItem.batch_id == batch_id)
    items = (await db.execute(query)).scalars().all()
    resumed: dict[str, list[str]] = {}
    for item in items:
        lease = await db.get(ProcessingLease, item.id)
        if lease and lease.expires_at > now:
            continue
        if lease:
            await db.delete(lease)
        if item.attempt_count >= settings.UPLOAD_MAX_ATTEMPTS:
            item.status = UploadItemStatus.FAILED.value
            item.error_code = "RETRY_LIMIT_REACHED"
            item.user_message = "Xử lý bị gián đoạn quá nhiều lần; cần recruiter kiểm tra thủ công."
            item.last_failure_at = now
        else:
            item.status = UploadItemStatus.QUEUED.value
            item.error_code = "INTERRUPTED_RECOVERED"
            item.user_message = "Đã phục hồi sau khi tiến trình bị gián đoạn."
            resumed.setdefault(item.batch_id, []).append(item.id)
        item.version += 1
    await db.flush()
    return resumed


async def reconcile_all_interrupted_items() -> dict[str, list[str]]:
    async with AsyncSessionLocal() as db:
        resumed = await reconcile_interrupted_items(db)
        await db.commit()
        return resumed

