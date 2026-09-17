# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.final_release import IdempotencyRecord


class IdempotencyConflict(ValueError):
    """Raised when a key is replayed with a different request payload."""


@dataclass(frozen=True)
class IdempotencyClaim:
    record: IdempotencyRecord
    replayed: bool


def request_fingerprint(payload: Any) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def claim_request(
    db: AsyncSession,
    *,
    actor_id: str,
    operation: str,
    idempotency_key: str,
    payload: Any,
) -> IdempotencyClaim:
    if not 8 <= len(idempotency_key) <= 128:
        raise ValueError("Idempotency-Key phải dài từ 8 đến 128 ký tự.")
    fingerprint = request_fingerprint(payload)
    existing = await db.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.actor_id == actor_id,
            IdempotencyRecord.operation == operation,
            IdempotencyRecord.idempotency_key == idempotency_key,
        )
    )
    if existing:
        if existing.request_fingerprint != fingerprint:
            raise IdempotencyConflict("Idempotency-Key đã được dùng với nội dung yêu cầu khác.")
        return IdempotencyClaim(existing, True)

    record = IdempotencyRecord(
        actor_id=actor_id,
        operation=operation,
        idempotency_key=idempotency_key,
        request_fingerprint=fingerprint,
        expires_at=datetime.utcnow() + timedelta(hours=settings.IDEMPOTENCY_TTL_HOURS),
    )
    db.add(record)
    await db.flush()
    return IdempotencyClaim(record, False)


async def complete_request(
    db: AsyncSession,
    record: IdempotencyRecord,
    *,
    resource_id: str | None,
    response_status: int,
    response_body: dict | list,
) -> None:
    record.resource_id = resource_id
    record.response_status = response_status
    record.response_body = response_body
    record.status = "COMPLETED"
    await db.flush()

