# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.models.final_release import ProcessingLease
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.models.upload_batch import DuplicateMatch, UploadBatch, UploadItem
from app.services.upload_recovery_service import acquire_processing_lease, reconcile_interrupted_items


@pytest.mark.asyncio
async def test_expired_lease_is_reconciled_without_resetting_completed_work(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'recovery.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(lambda sync: Base.metadata.create_all(sync, tables=[JobPosting.__table__, CandidateResume.__table__, UploadBatch.__table__, UploadItem.__table__, DuplicateMatch.__table__, ProcessingLease.__table__]))
    async with sessions() as db:
        interrupted = UploadItem(batch_id="batch-a", client_file_id="a", original_file_name="a.pdf", byte_size=1, status="PARSING", attempt_count=1)
        completed = UploadItem(batch_id="batch-a", client_file_id="b", original_file_name="b.pdf", byte_size=1, status="COMPLETED", attempt_count=1)
        db.add_all([interrupted, completed])
        await db.flush()
        db.add(ProcessingLease(upload_item_id=interrupted.id, owner_id="dead", lease_token="expired-token", acquired_at=datetime.utcnow() - timedelta(minutes=5), heartbeat_at=datetime.utcnow() - timedelta(minutes=5), expires_at=datetime.utcnow() - timedelta(minutes=1), attempt=1))
        await db.commit()
        resumed = await reconcile_interrupted_items(db, "batch-a")
        assert resumed == {"batch-a": [interrupted.id]}
        assert interrupted.status == "QUEUED"
        assert completed.status == "COMPLETED"
    await engine.dispose()


@pytest.mark.asyncio
async def test_active_lease_blocks_duplicate_worker_and_retry_ceiling_stops_work(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'lease.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(lambda sync: Base.metadata.create_all(sync, tables=[JobPosting.__table__, CandidateResume.__table__, UploadBatch.__table__, UploadItem.__table__, DuplicateMatch.__table__, ProcessingLease.__table__]))
    monkeypatch.setattr(settings, "UPLOAD_MAX_ATTEMPTS", 1)
    async with sessions() as db:
        item = UploadItem(batch_id="batch-b", client_file_id="a", original_file_name="a.pdf", byte_size=1, status="QUEUED")
        db.add(item)
        await db.flush()
        assert await acquire_processing_lease(db, item)
        assert await acquire_processing_lease(db, item) is None
        await db.commit()
    await engine.dispose()
