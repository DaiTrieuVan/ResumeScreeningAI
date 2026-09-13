# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from unittest.mock import AsyncMock

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
import app.models.upload_batch  # noqa: F401


@pytest_asyncio.fixture
async def batch_client(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'batches.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_db():
        async with sessions() as session:
            yield session
            await session.commit()

    process_mock = AsyncMock()
    monkeypatch.setattr("app.api.upload_batches.process_upload_batch", process_mock)
    app = FastAPI()
    app.include_router(recruiter_router, prefix="/api")
    app.dependency_overrides[get_db] = override_db

    async with sessions() as session:
        job = JobPosting(title="Batch Test", required_skills=["Python"])
        session.add(job)
        await session.commit()
        await session.refresh(job)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, job.id, process_mock
    await engine.dispose()


@pytest.mark.asyncio
async def test_batch_is_persisted_and_can_be_reloaded(batch_client):
    client, job_id, process_mock = batch_client
    response = await client.post(
        f"/api/recruiter/jobs/{job_id}/upload-batches",
        files=[("files", ("candidate.pdf", b"%PDF-1.4\nplaceholder", "application/pdf"))],
    )
    assert response.status_code == 202
    batch = response.json()
    assert batch["total_count"] == 1
    assert batch["items"][0]["status"] == "QUEUED"

    reloaded = await client.get(f"/api/recruiter/upload-batches/{batch['id']}")
    assert reloaded.status_code == 200
    assert reloaded.json()["items"][0]["original_file_name"] == "candidate.pdf"
    process_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_invalid_pdf_does_not_block_batch_and_is_retryable(batch_client):
    client, job_id, process_mock = batch_client
    response = await client.post(
        f"/api/recruiter/jobs/{job_id}/upload-batches",
        files=[
            ("files", ("valid.pdf", b"%PDF-1.4\nplaceholder", "application/pdf")),
            ("files", ("broken.pdf", b"not-a-pdf", "application/pdf")),
        ],
    )
    batch = response.json()
    assert batch["total_count"] == 2
    assert batch["failed_count"] == 1
    failed = next(item for item in batch["items"] if item["status"] == "FAILED")
    assert failed["error_code"] == "INVALID_PDF"

    retried = await client.post(
        f"/api/recruiter/upload-batches/{batch['id']}/retry",
        json={"scope": "SELECTED", "item_ids": [failed["id"]]},
        headers={"Idempotency-Key": "retry-invalid-pdf"},
    )
    assert retried.status_code == 202
    retry_item = next(item for item in retried.json()["items"] if item["id"] == failed["id"])
    assert retry_item["status"] == "QUEUED"
    assert process_mock.await_count == 2


@pytest.mark.asyncio
async def test_exact_duplicate_is_flagged_without_being_deleted(batch_client):
    client, job_id, _ = batch_client
    content = b"%PDF-1.4\nsame-candidate"
    response = await client.post(
        f"/api/recruiter/jobs/{job_id}/upload-batches",
        files=[
            ("files", ("candidate-a.pdf", content, "application/pdf")),
            ("files", ("candidate-copy.pdf", content, "application/pdf")),
        ],
    )
    batch = response.json()
    duplicate = next(item for item in batch["items"] if item["status"] == "DEDUPE_REVIEW")
    assert batch["duplicate_count"] == 1
    assert duplicate["duplicate_matches"][0]["match_type"] == "EXACT_FILE"
