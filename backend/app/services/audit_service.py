# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import hashlib
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent


SENSITIVE_KEYS = {"name", "email", "phone", "address", "raw_text", "excerpt", "cv", "resume", "new_value", "old_value"}


def redact_audit_value(value: Any) -> Any:
    if value is None:
        return None
    encoded = str(value).encode("utf-8")
    return {"redacted": True, "sha256": hashlib.sha256(encoded).hexdigest(), "length": len(encoded)}


def sanitize_audit_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in metadata.items():
        if any(marker in key.casefold() for marker in SENSITIVE_KEYS):
            sanitized[key] = redact_audit_value(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_audit_metadata(value)
        else:
            sanitized[key] = value
    return sanitized


def add_audit_event(
    db: AsyncSession,
    *,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    metadata: dict[str, Any] | None = None,
    resource_version: int | None = None,
    request_id: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        request_id=request_id,
        resource_version=resource_version,
        metadata_json=sanitize_audit_metadata(metadata or {}),
    )
    db.add(event)
    return event
