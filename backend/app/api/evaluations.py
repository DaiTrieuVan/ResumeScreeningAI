# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.final_release import EvaluationRun
from app.schemas.final_release import EvaluationRunRequest
from app.services.evaluation_service import execute_evaluation_run, serialize_evaluation_run


router = APIRouter(prefix="/evaluations", tags=["AI Evaluation"])


@router.post("/runs", status_code=status.HTTP_201_CREATED)
async def create_evaluation_run(payload: EvaluationRunRequest, db: AsyncSession = Depends(get_db)):
    dataset_path = Path(settings.EVALUATION_DATASET_DIR) / payload.dataset_version / "manifest.json"
    if not dataset_path.is_file():
        raise HTTPException(status_code=404, detail={"code": "DATASET_NOT_FOUND", "message": "Không tìm thấy phiên bản dataset."})
    try:
        run = await execute_evaluation_run(
            db,
            dataset_path=dataset_path,
            artifact_dir=settings.BENCHMARK_ARTIFACT_DIR,
            metadata=payload.model_dump(),
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail={"code": "INVALID_DATASET", "message": str(error)}) from error
    return await serialize_evaluation_run(db, run)


@router.get("/runs/{run_id}")
async def get_evaluation_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(EvaluationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Không tìm thấy lần đánh giá."})
    return await serialize_evaluation_run(db, run)

