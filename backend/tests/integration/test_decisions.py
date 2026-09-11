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
async def test_decisions_require_reason_detect_conflicts_and_preserve_history(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'decisions.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with sessions() as db:
        job = JobPosting(title="Decision", required_skills=[])
        db.add(job)
        await db.flush()
        resume = CandidateResume(job_id=job.id, file_name="cv.pdf", file_path="unused", file_size_bytes=10)
        db.add(resume)
        await db.flush()
        application = CandidateApplication(job_id=job.id, resume_id=resume.id, pipeline_stage="AI_ANALYZED", ai_recommendation="ADVANCE")
        db.add(application)
        await db.commit()

    async def override_db():
        async with sessions() as db:
            yield db
            await db.commit()

    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        missing_reason = await client.post(f"/api/recruiter/applications/{application.id}/decisions", headers={"If-Match": "1"}, json={"event_type": "HUMAN_DECISION", "decision": "REJECT", "to_stage": "REJECTED"})
        assert missing_reason.status_code == 422

        rejected = await client.post(f"/api/recruiter/applications/{application.id}/decisions", headers={"If-Match": "1"}, json={"event_type": "HUMAN_DECISION", "decision": "REJECT", "to_stage": "REJECTED", "reason_code": "SKILL_GAP", "note": "Thiếu kỹ năng bắt buộc"})
        assert rejected.status_code == 201
        assert rejected.json()["after_version"] == 2

        conflict = await client.post(f"/api/recruiter/applications/{application.id}/decisions", headers={"If-Match": "1"}, json={"event_type": "NOTE_ADDED", "note": "ghi chú cũ"})
        assert conflict.status_code == 409

        timeline = await client.get(f"/api/recruiter/applications/{application.id}/decisions")
        assert timeline.status_code == 200
        assert timeline.json()[0]["reason_code"] == "SKILL_GAP"
        detail = await client.get(f"/api/recruiter/applications/{application.id}")
        assert detail.json()["pipeline_stage"] == "REJECTED"
    await engine.dispose()
