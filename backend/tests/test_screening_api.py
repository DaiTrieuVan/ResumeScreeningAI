import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_and_list_jobs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "title": "Senior AI Engineer",
            "department": "AI Research",
            "required_skills": ["Python", "FastAPI", "PyTorch"],
            "min_years_experience": 4,
            "required_education": "Bachelor's Degree",
            "weight_skills": 0.5,
            "weight_experience": 0.35,
            "weight_education": 0.15
        }
        res = await ac.post("/api/jobs", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Senior AI Engineer"
        job_id = data["id"]

        res_list = await ac.get("/api/jobs")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 1
