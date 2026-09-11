import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.candidate_evaluation import CandidateApplication, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.repositories.candidate_query_repository import query_candidates
import app.models.recruiter_productivity  # noqa: F401
import app.models.screening_criteria  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.upload_batch  # noqa: F401


@pytest.mark.asyncio
async def test_candidate_query_combines_filters_sort_and_pagination(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'query.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with sessions() as db:
        job = JobPosting(title="Backend", required_skills=["Python"])
        db.add(job)
        await db.flush()
        for index in range(30):
            resume = CandidateResume(job_id=job.id, file_name=f"cv-{index}.pdf", file_path="unused", file_size_bytes=10, parsed_name=f"Python Candidate {index}", raw_text="Python FastAPI")
            db.add(resume)
            await db.flush()
            application = CandidateApplication(job_id=job.id, resume_id=resume.id, pipeline_stage="SHORTLISTED" if index % 2 == 0 else "AI_ANALYZED")
            db.add(application)
            await db.flush()
            db.add(ScreeningEvaluation(application_id=application.id, component_scores={}, overall_score=index, mandatory_gate="PASSED", input_fingerprint=f"q-{index}"))
        await db.commit()
        rows, total = await query_candidates(db, job.id, q="Python", stages=["SHORTLISTED"], min_score=10, sort="score_desc", page=1, page_size=10)
        assert total == 10
        assert len(rows) == 10
        assert rows[0][2].overall_score == 28
    await engine.dispose()
