from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.candidate_evaluation import CandidateApplication
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.models.upload_batch import UploadBatch
from app.repositories.recruiter_analytics_repository import get_recruiter_analytics
import app.models.recruiter_productivity  # noqa: F401
import app.models.recruitment_decision  # noqa: F401
import app.models.screening_criteria  # noqa: F401
import app.models.screening_result  # noqa: F401


@pytest.mark.asyncio
async def test_analytics_aggregate_funnel_quality_duration_and_overrides(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'analytics.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection: await connection.run_sync(Base.metadata.create_all)
    async with sessions() as db:
        job = JobPosting(title="Analytics", required_skills=[]); db.add(job); await db.flush()
        for index, stage in enumerate(["SHORTLISTED", "SHORTLISTED", "REJECTED"]):
            resume = CandidateResume(job_id=job.id, file_name=f"{index}.pdf", file_path="unused", file_size_bytes=1); db.add(resume); await db.flush()
            db.add(CandidateApplication(job_id=job.id, resume_id=resume.id, pipeline_stage=stage, ai_recommendation="ADVANCE", human_decision="REJECT" if index == 2 else "ADVANCE"))
        now = datetime.utcnow()
        db.add_all([
            UploadBatch(job_id=job.id, status="COMPLETED_WITH_ERRORS", total_count=10, success_count=7, failed_count=2, duplicate_count=1, created_at=now, completed_at=now + timedelta(seconds=10)),
            UploadBatch(job_id=job.id, status="COMPLETED", total_count=5, success_count=5, created_at=now, completed_at=now + timedelta(seconds=30)),
        ])
        await db.commit()
        result = await get_recruiter_analytics(db, job.id)
    assert result["funnel"] == {"REJECTED": 1, "SHORTLISTED": 2}
    assert result["upload_counts"]["success"] == 12
    assert result["median_processing_seconds"] == 20
    assert result["ai_override_rate"] == pytest.approx(1 / 3)
    await engine.dispose()
