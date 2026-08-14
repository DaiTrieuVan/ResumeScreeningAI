from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.screening_result import ScreeningResult

async def log_recruiter_feedback(
    db: AsyncSession,
    screening_id: str,
    status: str,
    feedback_notes: Optional[str] = None,
    score_override: Optional[float] = None
) -> Optional[ScreeningResult]:
    res = await db.execute(select(ScreeningResult).where(ScreeningResult.id == screening_id))
    s_result = res.scalar_one_or_none()
    if not s_result:
        return None
        
    s_result.recruiter_status = status
    if feedback_notes is not None:
        s_result.recruiter_feedback_notes = feedback_notes
    if score_override is not None:
        s_result.score_override = score_override
        s_result.overall_score = score_override
        
    await db.commit()
    await db.refresh(s_result)
    return s_result
