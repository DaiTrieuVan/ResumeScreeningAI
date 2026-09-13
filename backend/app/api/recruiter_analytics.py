# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.recruiter_analytics_repository import get_recruiter_analytics

router = APIRouter()


@router.get("/jobs/{job_id}/analytics")
async def recruiter_analytics(job_id: str, db: AsyncSession = Depends(get_db)):
    return await get_recruiter_analytics(db, job_id)
