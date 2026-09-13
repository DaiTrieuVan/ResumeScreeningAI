# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.models.candidate_evaluation import CandidateApplication
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.models.recruitment_decision import RecruitmentDecisionEvent
from app.models.screening_result import ScreeningResult
from app.services.candidate_privacy_service import anonymize_candidate, require_candidate_access
import app.models.audit_event  # noqa: F401
import app.models.recruiter_productivity  # noqa: F401
import app.models.recruitment_decision  # noqa: F401
import app.models.screening_criteria  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.upload_batch  # noqa: F401


def test_candidate_access_rejects_unknown_roles():
    with pytest.raises(PermissionError):
        require_candidate_access("viewer")


@pytest.mark.asyncio
async def test_anonymization_removes_pii_and_original_file(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_DIR", str(tmp_path))
    pdf = tmp_path / "private.pdf"; pdf.write_bytes(b"%PDF private")
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'privacy.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection: await connection.run_sync(Base.metadata.create_all)
    async with sessions() as db:
        job = JobPosting(title="Privacy", required_skills=[]); db.add(job); await db.flush()
        resume = CandidateResume(job_id=job.id, file_name=pdf.name, file_path=str(pdf), file_size_bytes=pdf.stat().st_size, parsed_name="Private Name", parsed_email="private@example.com", raw_text="secret CV"); db.add(resume); await db.flush()
        screening = ScreeningResult(job_id=job.id, resume_id=resume.id, skills_summary="Private Name knows Python", strengths_summary=["Private Name"], recruiter_feedback_notes="Call private@example.com"); db.add(screening)
        application = CandidateApplication(job_id=job.id, resume_id=resume.id); db.add(application); await db.flush()
        decision = RecruitmentDecisionEvent(application_id=application.id, event_type="NOTE", note="Private Name", actor_id="recruiter", before_version=1, after_version=1); db.add(decision); await db.flush()
        await anonymize_candidate(db, application.id, "privacy-admin")
        await db.commit()
        assert resume.parsed_email is None and resume.raw_text is None
        assert resume.parsed_name.startswith("Ứng viên ẩn danh")
        assert screening.skills_summary is None and screening.strengths_summary == []
        assert screening.recruiter_feedback_notes is None
        assert decision.note == "Đã ẩn danh theo chính sách lưu trữ."
        assert not Path(pdf).exists()
    await engine.dispose()
