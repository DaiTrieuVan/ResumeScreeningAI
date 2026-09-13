# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.core.database import AsyncSessionLocal, init_db, engine
from app.services.job_crawler_service import crawl_and_sync_jobs

import pytest

@pytest.mark.asyncio
async def test_service():
    print("=== 1. Testing DB Crawler Sync Service ===", flush=True)
    await init_db()
    async with AsyncSessionLocal() as db:
        new_added, updated, total_active = await crawl_and_sync_jobs(db, limit=5)
        print(f"CRAWL SERVICE RESULT: added={new_added}, updated={updated}, total={total_active}", flush=True)
        assert total_active >= 5
    await engine.dispose()

async def main():
    await test_service()
    print("\nALL CRAWLER VERIFICATION TESTS PASSED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
