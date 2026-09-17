# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.recruiter import router as recruiter_router
from app.core.config import settings
from app.core.database import Base, get_db
from app.models.audit_event import AuditEvent
from app.models.candidate_evaluation import CandidateApplication
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
import app.models.final_release  # noqa: F401
import app.models.recruiter_productivity  # noqa: F401
import app.models.recruitment_decision  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.upload_batch  # noqa: F401


@pytest_asyncio.fixture
async def privacy_client(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'privacy-contract.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_db():
        async with sessions() as session:
            yield session
            await session.commit()

    monkeypatch.setattr(settings, "STORAGE_DIR", str(tmp_path))
    app = FastAPI()
    app.include_router(recruiter_router, prefix="/api")
    app.dependency_overrides[get_db] = override_db

    pdf_path = tmp_path / "Nguyen-An-private.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nprivate fixture")
    async with sessions() as session:
        job = JobPosting(title="Blind review", required_skills=["Python"])
        session.add(job)
        await session.flush()
        resume = CandidateResume(
            job_id=job.id,
            file_name=pdf_path.name,
            file_path=str(pdf_path),
            file_size_bytes=pdf_path.stat().st_size,
            parsed_name="Nguyen An",
            parsed_email="an@example.com",
            parsed_phone="0901234567",
        )
        session.add(resume)
        await session.flush()
        application = CandidateApplication(job_id=job.id, resume_id=resume.id, pipeline_stage="RECRUITER_REVIEW")
        session.add(application)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, sessions, job.id, application.id
    await engine.dispose()


@pytest.mark.asyncio
async def test_privacy_policy_is_versioned_and_rejects_stale_update(privacy_client):
    client, _, job_id, _ = privacy_client
    initial = await client.get(f"/api/recruiter/jobs/{job_id}/review-privacy")
    assert initial.status_code == 200
    assert initial.json()["mode"] == "IDENTIFIED"

    updated = await client.put(
        f"/api/recruiter/jobs/{job_id}/review-privacy",
        headers={"If-Match": "1", "X-Actor-Id": "privacy-admin", "X-Actor-Role": "admin"},
        json={"mode": "BLIND", "reveal_stage": "HR_INTERVIEW"},
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    assert updated.json()["masked_fields"]

    stale = await client.put(
        f"/api/recruiter/jobs/{job_id}/review-privacy",
        headers={"If-Match": "1", "X-Actor-Role": "admin"},
        json={"mode": "IDENTIFIED"},
    )
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "VERSION_CONFLICT"


@pytest.mark.asyncio
async def test_blind_resume_requires_authorized_explicit_reveal_and_audits_it(privacy_client):
    client, sessions, job_id, application_id = privacy_client
    await client.put(
        f"/api/recruiter/jobs/{job_id}/review-privacy",
        headers={"If-Match": "1", "X-Actor-Role": "admin"},
        json={"mode": "BLIND"},
    )

    hidden = await client.get(f"/api/recruiter/applications/{application_id}/resume")
    assert hidden.status_code == 403
    denied = await client.get(
        f"/api/recruiter/applications/{application_id}/resume?reveal=true",
        headers={"X-Actor-Role": "viewer"},
    )
    assert denied.status_code == 403

    revealed = await client.get(
        f"/api/recruiter/applications/{application_id}/resume?reveal=true",
        headers={"X-Actor-Id": "reviewer-1", "X-Actor-Role": "recruiter"},
    )
    assert revealed.status_code == 200
    async with sessions() as session:
        event = await session.scalar(
            select(AuditEvent).where(AuditEvent.action == "REVEAL_ORIGINAL_RESUME")
        )
        assert event is not None
        assert event.actor_id == "reviewer-1"
        assert "an@example.com" not in str(event.metadata_json)
        assert "Nguyen An" not in str(event.metadata_json)
