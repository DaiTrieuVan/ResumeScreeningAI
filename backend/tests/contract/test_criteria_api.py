import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.recruiter import router as recruiter_router
from app.core.database import Base, get_db
from app.models.job_posting import JobPosting
import app.models.audit_event  # noqa: F401
import app.models.candidate_resume  # noqa: F401
import app.models.screening_result  # noqa: F401
import app.models.screening_criteria  # noqa: F401


@pytest_asyncio.fixture
async def criteria_client(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'criteria.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_db():
        async with sessions() as session:
            yield session
            await session.commit()

    app = FastAPI()
    app.include_router(recruiter_router, prefix="/api")
    app.dependency_overrides[get_db] = override_db

    async with sessions() as session:
        job = JobPosting(title="Backend Engineer", required_skills=["Python"])
        session.add(job)
        await session.commit()
        await session.refresh(job)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, job.id
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_publish_criteria_version(criteria_client):
    client, job_id = criteria_client
    payload = {
        "name": "Backend scorecard",
        "scoring_weights": {"skills": 0.5, "experience": 0.3, "education": 0.2},
        "criteria": [
            {
                "category": "SKILL",
                "importance": "MANDATORY",
                "label": "Python",
                "operator": "CONTAINS_ANY",
                "expected_value": ["Python"],
                "weight": 0.5,
            }
        ],
    }
    created = await client.post(f"/api/recruiter/jobs/{job_id}/criteria-sets", json=payload)
    assert created.status_code == 201
    assert created.json()["status"] == "DRAFT"

    published = await client.post(
        f"/api/recruiter/criteria-sets/{created.json()['id']}/publish",
        headers={"If-Match": "1"},
    )
    assert published.status_code == 200
    assert published.json()["status"] == "PUBLISHED"


@pytest.mark.asyncio
async def test_publish_rejects_invalid_weight_total(criteria_client):
    client, job_id = criteria_client
    created = await client.post(
        f"/api/recruiter/jobs/{job_id}/criteria-sets",
        json={
            "name": "Invalid draft",
            "scoring_weights": {"skills": 0.5, "experience": 0.3, "education": 0.15},
            "criteria": [],
        },
    )
    response = await client.post(
        f"/api/recruiter/criteria-sets/{created.json()['id']}/publish",
        headers={"If-Match": "1"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_CRITERIA_WEIGHTS"
