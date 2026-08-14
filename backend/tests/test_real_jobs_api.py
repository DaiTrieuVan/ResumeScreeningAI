import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()

@pytest.mark.asyncio
async def test_list_real_jobs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/real-jobs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    assert any(j["source"] in ["TopCV", "ITViec"] for j in data)

@pytest.mark.asyncio
async def test_match_cv_with_real_jobs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/real-jobs/match", data={"cv_text": "Lập trình viên Senior Python, FastAPI, Docker, PostgreSQL, React 4 năm kinh nghiệm tại Hà Nội"})
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) > 0
    assert matches[0]["match_score"] > 0
