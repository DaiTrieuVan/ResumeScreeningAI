# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.evaluations import router
from app.core.config import settings
from app.core.database import Base, get_db
from app.models.final_release import EvaluationRun, MetricResult


@pytest_asyncio.fixture
async def evaluation_client(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[3]
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'evaluation.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(
            lambda sync_connection: Base.metadata.create_all(
                sync_connection, tables=[EvaluationRun.__table__, MetricResult.__table__]
            )
        )

    async def override_db():
        async with sessions() as session:
            yield session
            await session.commit()

    monkeypatch.setattr(settings, "EVALUATION_DATASET_DIR", str(root / "evaluation" / "datasets"))
    monkeypatch.setattr(settings, "BENCHMARK_ARTIFACT_DIR", str(tmp_path / "reports"))
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await engine.dispose()


@pytest.mark.asyncio
async def test_evaluation_run_is_traceable_and_reports_measured_counts(evaluation_client):
    response = await evaluation_client.post("/api/evaluations/runs", json={
        "dataset_version": "competition-v1",
        "release_version": "0.9.0-rc.1",
        "commit_sha": "9a9ae25",
        "fallback_mode": True,
        "model_metadata": {"name": "deterministic-offline-v1"},
    })
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PASSED"
    assert body["dataset_version"] == "competition-v1"
    assert body["commit_sha"] == "9a9ae25"
    assert len(body["metrics"]) == 5
    assert all(metric["denominator"] > 0 for metric in body["metrics"])

    fetched = await evaluation_client.get(f"/api/evaluations/runs/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["metrics"] == body["metrics"]

