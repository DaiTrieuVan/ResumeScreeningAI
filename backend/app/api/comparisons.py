from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.comparison_service import ComparisonConflictError, compare_candidates

router = APIRouter()


class ComparisonInput(BaseModel):
    application_ids: list[str] = Field(min_length=2, max_length=5)
    criteria_set_id: str


@router.post("/jobs/{job_id}/comparisons")
async def create_comparison(job_id: str, payload: ComparisonInput, db: AsyncSession = Depends(get_db)):
    if len(set(payload.application_ids)) != len(payload.application_ids):
        raise HTTPException(422, detail={"code": "DUPLICATE_APPLICATION", "message": "Mỗi ứng viên chỉ được chọn một lần."})
    try:
        return await compare_candidates(db, job_id, payload.application_ids, payload.criteria_set_id)
    except LookupError as error:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ComparisonConflictError as error:
        raise HTTPException(409, detail={"code": "CRITERIA_VERSION_MISMATCH", "message": str(error)}) from error
