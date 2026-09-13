from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.screening_criteria import (
    CriteriaSetInput,
    CriteriaSetResponse,
    ScoreSimulationInput,
    ScoreSimulationResponse,
)
from app.services.criteria_service import (
    CriteriaValidationError,
    create_criteria_draft,
    list_criteria_sets,
    publish_criteria_set,
    validate_scoring_weights,
)
from app.services.scoring_service import calculate_weighted_score


router = APIRouter()


def _not_found(error: LookupError) -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(error)})


@router.get("/jobs/{job_id}/criteria-sets", response_model=list[CriteriaSetResponse])
async def get_job_criteria_sets(job_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await list_criteria_sets(db, job_id)
    except LookupError as error:
        raise _not_found(error) from error


@router.post(
    "/jobs/{job_id}/criteria-sets",
    response_model=CriteriaSetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_criteria_set(
    job_id: str,
    payload: CriteriaSetInput,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await create_criteria_draft(db, job_id, payload)
    except LookupError as error:
        raise _not_found(error) from error


@router.post(
    "/criteria-sets/{criteria_set_id}/publish",
    response_model=CriteriaSetResponse,
)
async def publish_job_criteria_set(
    criteria_set_id: str,
    if_match: str = Header(..., alias="If-Match"),
    db: AsyncSession = Depends(get_db),
):
    try:
        expected_version = int(if_match.strip('"'))
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_ETAG", "message": "If-Match phải là version của vị trí."},
        ) from error
    try:
        return await publish_criteria_set(db, criteria_set_id, expected_version)
    except LookupError as error:
        raise _not_found(error) from error
    except CriteriaValidationError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_CRITERIA_WEIGHTS",
                "message": str(error),
                "field_errors": error.field_errors,
            },
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=409,
            detail={"code": "VERSION_CONFLICT", "message": str(error)},
        ) from error


@router.post("/score-simulations", response_model=ScoreSimulationResponse)
async def simulate_score(payload: ScoreSimulationInput):
    try:
        validate_scoring_weights(payload.proposed_weights)
    except CriteriaValidationError as error:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_CRITERIA_WEIGHTS", "message": str(error), "field_errors": error.field_errors},
        ) from error
    return ScoreSimulationResponse(
        score=calculate_weighted_score(payload.component_scores, payload.proposed_weights)
    )
