import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.recruiter import router as recruiter_router
from app.core.config import settings
from app.core.database import Base, get_db
from app.models.candidate_evaluation import CandidateApplication, CriterionResult, EvidenceSnippet, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.models.screening_criteria import Criterion, ScreeningCriteriaSet
import app.models.audit_event  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.upload_batch  # noqa: F401


@pytest_asyncio.fixture
async def candidate_client(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'candidate.db'}")
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

    pdf_path = tmp_path / "candidate.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nresume")
    async with sessions() as session:
        job = JobPosting(title="Evidence Test", required_skills=["Python"])
        session.add(job)
        await session.flush()
        resume = CandidateResume(
            job_id=job.id, file_name="candidate.pdf", file_path=str(pdf_path), file_size_bytes=pdf_path.stat().st_size,
            raw_text="Python and FastAPI", parsed_name="Nguyen An", parsed_email="an@example.com",
        )
        session.add(resume)
        await session.flush()
        criteria_set = ScreeningCriteriaSet(
            job_id=job.id, version_number=1, name="v1", status="PUBLISHED",
            scoring_weights={"skills": 1.0}, criteria=[],
        )
        criterion = Criterion(
            category="SKILL", importance="MANDATORY", label="Python",
            operator="CONTAINS_ANY", expected_value=["Python"], weight=1, sort_order=0,
        )
        criteria_set.criteria.append(criterion)
        session.add(criteria_set)
        await session.flush()
        application = CandidateApplication(job_id=job.id, resume_id=resume.id, pipeline_stage="AI_ANALYZED")
        session.add(application)
        await session.flush()
        evaluation = ScreeningEvaluation(
            application_id=application.id, criteria_set_id=criteria_set.id,
            component_scores={"skills": 90}, overall_score=90, mandatory_gate="PASSED",
            input_fingerprint="evidence-contract", evidence_status="AVAILABLE", criterion_results=[],
        )
        result = CriterionResult(
            criterion_id=criterion.id, label="Python", importance="MANDATORY", result="MET",
            score=100, confidence=0.95, explanation="Có bằng chứng", evidence=[],
        )
        result.evidence.append(EvidenceSnippet(
            resume_id=resume.id, start_offset=0, end_offset=6, excerpt="Python and FastAPI",
            polarity="SUPPORTS", confidence=0.95,
        ))
        evaluation.criterion_results.append(result)
        session.add(evaluation)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, application.id
    await engine.dispose()


@pytest.mark.asyncio
async def test_candidate_detail_contains_verifiable_evidence(candidate_client):
    client, application_id = candidate_client
    response = await client.get(f"/api/recruiter/applications/{application_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["candidate_name"] == "Nguyen An"
    assert detail["evaluation"]["criterion_results"][0]["result"] == "MET"
    assert detail["evaluation"]["criterion_results"][0]["evidence"][0]["excerpt"] == "Python and FastAPI"


@pytest.mark.asyncio
async def test_original_resume_opens_inline(candidate_client):
    client, application_id = candidate_client
    response = await client.get(f"/api/recruiter/applications/{application_id}/resume")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.headers["content-disposition"].startswith("inline")
