# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.recruiter import router
from app.core.database import Base, get_db
from app.models.candidate_evaluation import CandidateApplication
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
import app.models.recruiter_productivity  # noqa: F401
import app.models.screening_criteria  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.upload_batch  # noqa: F401


@pytest.mark.asyncio
async def test_bulk_action_is_idempotent_and_reports_version_conflicts(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'bulk.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with sessions() as db:
        job = JobPosting(title="Bulk", required_skills=[])
        db.add(job)
        await db.flush()
        resume = CandidateResume(job_id=job.id, file_name="cv.pdf", file_path="unused", file_size_bytes=10)
        db.add(resume)
        await db.flush()
        application = CandidateApplication(job_id=job.id, resume_id=resume.id, version=2)
        db.add(application)
        await db.commit()

    async def override_db():
        async with sessions() as db:
            yield db
            await db.commit()
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_db] = override_db
    payload = {"action": "MOVE_STAGE", "application_ids": [application.id], "expected_versions": {application.id: 1}, "value": "SHORTLISTED"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post(f"/api/recruiter/jobs/{job.id}/bulk-actions", headers={"Idempotency-Key": "bulk-test-key"}, json=payload)
        second = await client.post(f"/api/recruiter/jobs/{job.id}/bulk-actions", headers={"Idempotency-Key": "bulk-test-key"}, json=payload)
    assert first.status_code == 202
    assert first.json()["items"][0]["error_code"] == "VERSION_CONFLICT"
    assert second.json()["id"] == first.json()["id"]
    await engine.dispose()
