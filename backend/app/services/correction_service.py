# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_evaluation import CandidateApplication
from app.models.candidate_resume import CandidateResume
from app.models.final_release import CandidateCorrection
from app.schemas.final_release import CORRECTABLE_FIELDS
from app.services.audit_service import add_audit_event, redact_audit_value
from app.services.idempotency_service import claim_request, complete_request


LIST_FIELDS = {"extracted_skills", "work_history", "education"}


async def correct_candidate(
    db: AsyncSession,
    *,
    application_id: str,
    expected_version: int,
    field_path: str,
    new_value: Any,
    reason: str,
    actor_id: str,
    idempotency_key: str,
    evidence_id: str | None = None,
) -> dict:
    if field_path not in CORRECTABLE_FIELDS:
        raise ValueError("Trường dữ liệu này không được phép chỉnh sửa.")
    if field_path in LIST_FIELDS and not isinstance(new_value, list):
        raise ValueError("Giá trị trường danh sách phải là một mảng.")
    if field_path not in LIST_FIELDS and new_value is not None and not isinstance(new_value, str):
        raise ValueError("Giá trị trường thông tin phải là chuỗi hoặc null.")

    claim = await claim_request(
        db, actor_id=actor_id, operation="CORRECT_PROFILE", idempotency_key=idempotency_key,
        payload={"application_id": application_id, "field_path": field_path, "new_value": new_value, "reason": reason, "evidence_id": evidence_id},
    )
    if claim.replayed and claim.record.status == "COMPLETED":
        return claim.record.response_body

    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise LookupError("Không tìm thấy hồ sơ ứng viên.")
    if application.version != expected_version:
        raise RuntimeError("Hồ sơ đã thay đổi; vui lòng tải lại trước khi sửa.")
    resume = await db.get(CandidateResume, application.resume_id)
    if not resume:
        raise LookupError("Không tìm thấy CV ứng viên.")

    old_value = getattr(resume, field_path)
    setattr(resume, field_path, new_value)
    correction = CandidateCorrection(
        resume_id=resume.id,
        application_id=application.id,
        field_path=field_path,
        old_value_redacted=redact_audit_value(old_value),
        new_value=new_value,
        reason=reason,
        actor_id=actor_id,
        evidence_id=evidence_id,
        affects_evaluation=True,
    )
    db.add(correction)
    application.version += 1
    application.evaluation_stale = True
    application.stale_reason = f"Dữ liệu {field_path} đã được recruiter hiệu chỉnh."
    audit = add_audit_event(
        db,
        actor_id=actor_id,
        action="CORRECT_CANDIDATE_PROFILE",
        resource_type="CandidateApplication",
        resource_id=application.id,
        resource_version=application.version,
        metadata={"field_path": field_path, "old_value": old_value, "new_value": new_value, "reason": reason},
    )
    await db.flush()
    response = {
        "application_id": application.id,
        "application_version": application.version,
        "evaluation_stale": True,
        "audit_event_id": audit.id,
    }
    await complete_request(db, claim.record, resource_id=application.id, response_status=200, response_body=response)
    return response
