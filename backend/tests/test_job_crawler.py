# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()

@pytest.mark.asyncio
async def test_crawl_real_jobs_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/real-jobs/crawl?limit=5")
    
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "new_jobs_added" in data
    assert "existing_jobs_updated" in data
    assert data["total_active_jobs"] >= 5

@pytest.mark.asyncio
async def test_real_jobs_list_after_crawl():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/api/real-jobs/crawl?limit=5")
        res = await ac.get("/api/real-jobs")
    
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) >= 5
