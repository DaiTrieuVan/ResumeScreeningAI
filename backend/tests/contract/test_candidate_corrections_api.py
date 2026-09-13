# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.recruiter import router as recruiter_router
from app.core.database import Base, get_db
from app.models.audit_event import AuditEvent
from app.models.candidate_evaluation import CandidateApplication
from app.models.candidate_resume import CandidateResume
from app.models.final_release import CandidateCorrection, IdempotencyRecord
from app.models.job_posting import JobPosting
import app.models.recruitment_decision  # noqa: F401
import app.models.recruiter_productivity  # noqa: F401
import app.models.screening_criteria  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.upload_batch  # noqa: F401


@pytest_asyncio.fixture
async def correction_client(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'correction.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_db():
        async with sessions() as session:
            yield session
            await session.commit()

    async with sessions() as session:
        job = JobPosting(title="Backend", required_skills=["Python"])
        session.add(job)
        await session.flush()
        resume = CandidateResume(job_id=job.id, file_name="cv.pdf", file_path="cv.pdf", file_size_bytes=1, raw_text="Python", parsed_name="Old Name")
        session.add(resume)
        await session.flush()
        application = CandidateApplication(job_id=job.id, resume_id=resume.id)
        session.add(application)
        await session.commit()
        application_id = application.id

    app = FastAPI()
    app.include_router(recruiter_router, prefix="/api")
    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, sessions, application_id
    await engine.dispose()


@pytest.mark.asyncio
async def test_correction_is_audited_redacted_and_marks_application_stale(correction_client):
    client, sessions, application_id = correction_client
    response = await client.post(
        f"/api/recruiter/applications/{application_id}/corrections",
        headers={"If-Match": "1", "Idempotency-Key": "correction-test-1", "X-Actor-Id": "judge-demo", "X-Actor-Role": "recruiter"},
        json={"field_path": "parsed_name", "new_value": "Correct Name", "reason": "Verified against CV"},
    )
    assert response.status_code == 200
    assert response.json()["evaluation_stale"] is True

    async with sessions() as session:
        application = await session.get(CandidateApplication, application_id)
        resume = await session.get(CandidateResume, application.resume_id)
        correction = await session.scalar(select(CandidateCorrection))
        audit = await session.scalar(select(AuditEvent).where(AuditEvent.action == "CORRECT_CANDIDATE_PROFILE"))
        assert resume.parsed_name == "Correct Name"
        assert application.evaluation_stale is True
        assert correction.old_value_redacted["redacted"] is True
        assert audit.metadata_json["new_value"]["redacted"] is True


@pytest.mark.asyncio
async def test_correction_rejects_stale_version(correction_client):
    client, _, application_id = correction_client
    response = await client.post(
        f"/api/recruiter/applications/{application_id}/corrections",
        headers={"If-Match": "99", "Idempotency-Key": "correction-test-2", "X-Actor-Role": "recruiter"},
        json={"field_path": "parsed_name", "new_value": "Name", "reason": "Verified"},
    )
    assert response.status_code == 409

