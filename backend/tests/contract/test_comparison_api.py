import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.recruiter import router
from app.core.database import Base, get_db
from app.models.candidate_evaluation import CandidateApplication, CriterionResult, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.models.screening_criteria import Criterion, ScreeningCriteriaSet
import app.models.recruiter_productivity  # noqa: F401
import app.models.recruitment_decision  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.upload_batch  # noqa: F401


@pytest.mark.asyncio
async def test_comparison_aligns_candidates_on_one_criteria_version(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'comparison.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    ids = []
    async with sessions() as db:
        job = JobPosting(title="Compare", required_skills=["Python"])
        db.add(job); await db.flush()
        criteria_set = ScreeningCriteriaSet(job_id=job.id, version_number=1, name="v1", status="PUBLISHED", scoring_weights={"skills": 1}, criteria=[])
        criterion = Criterion(category="SKILL", importance="MANDATORY", label="Python", operator="CONTAINS_ANY", expected_value=["Python"], weight=1, sort_order=0)
        criteria_set.criteria.append(criterion); db.add(criteria_set); await db.flush()
        for index, outcome in enumerate(["MET", "UNKNOWN"]):
            resume = CandidateResume(job_id=job.id, file_name=f"cv-{index}.pdf", file_path="unused", file_size_bytes=10, parsed_name=f"Candidate {index}")
            db.add(resume); await db.flush()
            application = CandidateApplication(job_id=job.id, resume_id=resume.id, pipeline_stage="SHORTLISTED")
            db.add(application); await db.flush(); ids.append(application.id)
            evaluation = ScreeningEvaluation(application_id=application.id, criteria_set_id=criteria_set.id, component_scores={"skills": 90-index*20}, overall_score=90-index*20, mandatory_gate="PASSED" if outcome == "MET" else "NEEDS_REVIEW", input_fingerprint=f"compare-{index}", criterion_results=[])
            evaluation.criterion_results.append(CriterionResult(criterion_id=criterion.id, label="Python", importance="MANDATORY", result=outcome, confidence=.9 if outcome == "MET" else .2, explanation="source" if outcome == "MET" else "missing", evidence=[]))
            db.add(evaluation)
        await db.commit()

    async def override_db():
        async with sessions() as db:
            yield db; await db.commit()
    app = FastAPI(); app.include_router(router, prefix="/api"); app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/api/recruiter/jobs/{job.id}/comparisons", json={"application_ids": ids, "criteria_set_id": criteria_set.id})
    assert response.status_code == 200
    body = response.json()
    assert len(body["candidates"]) == 2
    assert body["criteria"][0]["results"][ids[1]]["result"] == "UNKNOWN"
    await engine.dispose()
