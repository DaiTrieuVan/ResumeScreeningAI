# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.job_posting import JobPosting
from app.core.database import init_db, AsyncSessionLocal
from sqlalchemy import select

created_job_ids = []

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()
    yield
    if created_job_ids:
        async with AsyncSessionLocal() as db:
            for jid in created_job_ids:
                job_res = await db.execute(select(JobPosting).where(JobPosting.id == jid))
                job = job_res.scalar_one_or_none()
                if job:
                    await db.delete(job)
            await db.commit()
            created_job_ids.clear()

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
        created_job_ids.append(job_id)

        res_list = await ac.get("/api/jobs")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 1

@pytest.mark.asyncio
async def test_evaluate_stream():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_res = await ac.post("/api/jobs", json={
            "title": "Backend Streaming Tester",
            "department": "Engineering",
            "required_skills": ["Python", "FastAPI"],
            "min_years_experience": 2
        })
        job_id = job_res.json()["id"]
        created_job_ids.append(job_id)

        res = await ac.post("/api/screenings/evaluate/stream", json={"job_id": job_id})
        assert res.status_code == 200
        assert "text/event-stream" in res.headers.get("content-type", "")
        assert "data: " in res.text

@pytest.mark.asyncio
async def test_upload_and_evaluate_by_job_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        job_res = await ac.post("/api/jobs", json={
            "title": "Specific Job AI",
            "department": "Engineering",
            "required_skills": ["Python"]
        })
        job_id = job_res.json()["id"]
        created_job_ids.append(job_id)

        # Upload dummy PDF for specific job
        files = [("files", ("test_cv.pdf", b"%PDF-1.4 test pdf content", "application/pdf"))]
        data = {"job_id": job_id}
        upload_res = await ac.post("/api/resumes/upload", files=files, data=data)
        assert upload_res.status_code == 200
        uploaded = upload_res.json()
        assert len(uploaded) == 1
        assert uploaded[0]["job_id"] == job_id
