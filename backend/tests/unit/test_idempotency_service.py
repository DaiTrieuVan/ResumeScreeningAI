# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.final_release import IdempotencyRecord
from app.services.idempotency_service import IdempotencyConflict, claim_request, complete_request


@pytest.mark.asyncio
async def test_same_key_replays_completed_result_and_different_payload_conflicts(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'idempotency.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(lambda sync: Base.metadata.create_all(sync, tables=[IdempotencyRecord.__table__]))
    async with sessions() as db:
        first = await claim_request(db, actor_id="actor", operation="RETRY", idempotency_key="same-key-123", payload={"item": 1})
        await complete_request(db, first.record, resource_id="resource", response_status=202, response_body={"ok": True})
        await db.commit()
    async with sessions() as db:
        replay = await claim_request(db, actor_id="actor", operation="RETRY", idempotency_key="same-key-123", payload={"item": 1})
        assert replay.replayed is True
        assert replay.record.response_body == {"ok": True}
        with pytest.raises(IdempotencyConflict):
            await claim_request(db, actor_id="actor", operation="RETRY", idempotency_key="same-key-123", payload={"item": 2})
    await engine.dispose()

