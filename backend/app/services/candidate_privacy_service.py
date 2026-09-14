# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import hashlib
import re
from pathlib import Path

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.audit_event import AuditEvent
from app.models.candidate_evaluation import CandidateApplication, CriterionResult, EvidenceSnippet, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume
from app.models.recruitment_decision import RecruitmentDecisionEvent
from app.models.screening_result import ScreeningResult
from app.models.final_release import ReviewPrivacyPolicy
from app.services.audit_service import add_audit_event


ALLOWED_PII_ROLES = {"system", "recruiter", "hiring_manager", "admin"}
MASKED_FIELDS = ["name", "email", "phone", "photo", "address", "file_name", "employer", "school"]
EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?:\+?\d[\d .()-]{7,}\d)")
MASKED_VALUE = "[ĐÃ ẨN]"


def require_candidate_access(actor_role: str | None) -> None:
    if (actor_role or "").casefold() not in ALLOWED_PII_ROLES:
        raise PermissionError("Bạn không có quyền truy cập dữ liệu cá nhân của ứng viên.")


def record_candidate_access(db: AsyncSession, application: CandidateApplication, actor_id: str, action: str) -> None:
    db.add(AuditEvent(actor_id=actor_id, action=action, resource_type="CandidateApplication", resource_id=application.id, resource_version=application.version, metadata_json={"job_id": application.job_id}))


def anonymous_candidate_name(application_id: str) -> str:
    return f"Ứng viên {hashlib.sha256(application_id.encode()).hexdigest()[:8].upper()}"


def redact_identifiers(text: str | None, identifiers: list[str] | tuple[str, ...] = ()) -> str | None:
    if not text:
        return text
    redacted = PHONE_PATTERN.sub("[SỐ ĐIỆN THOẠI ĐÃ ẨN]", EMAIL_PATTERN.sub("[EMAIL ĐÃ ẨN]", text))
    for identifier in sorted({value.strip() for value in identifiers if value and len(value.strip()) >= 3}, key=len, reverse=True):
        redacted = re.sub(re.escape(identifier), MASKED_VALUE, redacted, flags=re.IGNORECASE)
    return redacted


def candidate_identifiers(resume: CandidateResume) -> list[str]:
    identifiers = [resume.parsed_name, resume.parsed_email, resume.parsed_phone, resume.file_name]
    for entry in resume.work_history or []:
        if isinstance(entry, dict):
            identifiers.extend([entry.get("employer"), entry.get("company"), entry.get("organization")])
    for entry in resume.education or []:
        if isinstance(entry, dict):
            identifiers.extend([entry.get("school"), entry.get("institution"), entry.get("university")])
    return [value for value in identifiers if isinstance(value, str) and value.strip()]


def _mask_nested(value, identifiers: list[str], key: str | None = None):
    normalized_key = (key or "").casefold()
    if normalized_key in {"candidate_email", "candidate_phone", "parsed_email", "parsed_phone", "email", "phone"}:
        return None
    if normalized_key in {"employer", "company", "organization", "school", "institution", "university", "address", "photo"}:
        return MASKED_VALUE
    if isinstance(value, dict):
        return {child_key: _mask_nested(child_value, identifiers, child_key) for child_key, child_value in value.items()}
    if isinstance(value, list):
        return [_mask_nested(item, identifiers) for item in value]
    if isinstance(value, str):
        return redact_identifiers(value, identifiers)
    return value


def mask_sensitive_payload(payload, identifiers: list[str] | None = None):
    return _mask_nested(payload, identifiers or [])


async def get_review_privacy_policy(db: AsyncSession, job_id: str) -> ReviewPrivacyPolicy:
    policy = await db.get(ReviewPrivacyPolicy, job_id)
    if policy:
        return policy
    policy = ReviewPrivacyPolicy(
        job_id=job_id,
        mode=settings.DEFAULT_REVIEW_PRIVACY_MODE,
        masked_fields=MASKED_FIELDS,
    )
    db.add(policy)
    await db.flush()
    return policy


async def update_review_privacy_policy(db: AsyncSession, job_id: str, mode: str, reveal_stage: str | None, expected_version: int, actor_id: str) -> ReviewPrivacyPolicy:
    policy = await get_review_privacy_policy(db, job_id)
    if policy.version != expected_version:
        raise RuntimeError("Chính sách đã thay đổi; vui lòng tải lại.")
    policy.mode = mode
    policy.reveal_stage = reveal_stage
    policy.updated_by = actor_id
    policy.version += 1
    add_audit_event(db, actor_id=actor_id, action="UPDATE_REVIEW_PRIVACY", resource_type="JobPosting", resource_id=job_id, resource_version=policy.version, metadata={"mode": mode, "reveal_stage": reveal_stage})
    await db.flush()
    return policy


def mask_candidate_projection(application_id: str, payload: dict, identifiers: list[str] | None = None) -> dict:
    identifiers = identifiers or []
    masked = mask_sensitive_payload(payload, identifiers)
    masked["candidate_name"] = anonymous_candidate_name(application_id)
    masked["candidate_email"] = None
    masked["candidate_phone"] = None
    masked["file_name"] = f"hoso-{application_id[:8]}.pdf"
    return masked


async def anonymize_candidate(db: AsyncSession, application_id: str, actor_id: str = "system"):
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise LookupError("Không tìm thấy hồ sơ ứng viên.")
    resume = await db.get(CandidateResume, application.resume_id)
    if not resume:
        raise LookupError("Không tìm thấy CV ứng viên.")
    storage_root = Path(settings.STORAGE_DIR).resolve()
    file_path = Path(resume.file_path).resolve() if resume.file_path else None
    if file_path and file_path.is_relative_to(storage_root) and file_path.is_file():
        file_path.unlink()
    anonymous_key = hashlib.sha256(application.id.encode()).hexdigest()[:12]
    resume.parsed_name = f"Ứng viên ẩn danh {anonymous_key}"
    resume.parsed_email = None
    resume.parsed_phone = None
    resume.raw_text = None
    resume.extracted_skills = []
    resume.work_history = []
    resume.education = []
    resume.file_name = f"anonymized-{anonymous_key}.pdf"
    resume.file_path = ""

    # Evidence and free-text summaries are derived from the original CV and may
    # repeat names, contact details, or other identifying information.
    await db.execute(delete(EvidenceSnippet).where(EvidenceSnippet.resume_id == resume.id))
    evaluation_ids = select(ScreeningEvaluation.id).where(ScreeningEvaluation.application_id == application.id)
    await db.execute(
        update(CriterionResult)
        .where(CriterionResult.evaluation_id.in_(evaluation_ids))
        .values(explanation="Đã ẩn danh theo chính sách lưu trữ.")
    )
    await db.execute(
        update(ScreeningResult)
        .where(ScreeningResult.resume_id == resume.id)
        .values(
            skills_summary=None,
            experience_summary=None,
            education_summary=None,
            strengths_summary=[],
            gaps_summary=[],
            ai_reasoning=None,
            recruiter_feedback_notes=None,
        )
    )
    await db.execute(
        update(RecruitmentDecisionEvent)
        .where(RecruitmentDecisionEvent.application_id == application.id)
        .values(note="Đã ẩn danh theo chính sách lưu trữ.")
    )
    application.version += 1
    record_candidate_access(db, application, actor_id, "ANONYMIZE_CANDIDATE")
    await db.flush()
    return application
