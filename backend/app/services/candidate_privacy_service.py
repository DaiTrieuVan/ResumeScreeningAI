# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import hashlib
from pathlib import Path

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.audit_event import AuditEvent
from app.models.candidate_evaluation import CandidateApplication, CriterionResult, EvidenceSnippet, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume
from app.models.recruitment_decision import RecruitmentDecisionEvent
from app.models.screening_result import ScreeningResult


ALLOWED_PII_ROLES = {"system", "recruiter", "hiring_manager", "admin"}


def require_candidate_access(actor_role: str | None) -> None:
    if (actor_role or "").casefold() not in ALLOWED_PII_ROLES:
        raise PermissionError("Bạn không có quyền truy cập dữ liệu cá nhân của ứng viên.")


def record_candidate_access(db: AsyncSession, application: CandidateApplication, actor_id: str, action: str) -> None:
    db.add(AuditEvent(actor_id=actor_id, action=action, resource_type="CandidateApplication", resource_id=application.id, resource_version=application.version, metadata_json={"job_id": application.job_id}))


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
