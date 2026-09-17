# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.schemas.final_release import ReviewPrivacyPolicyUpdate
from app.services.candidate_privacy_service import get_review_privacy_policy, update_review_privacy_policy


router = APIRouter(prefix="/recruiter", tags=["Recruiter Workspace"])


@router.get("/health")
async def recruiter_health() -> dict[str, str]:
    return {"status": "healthy", "workspace": "recruiter-v2", "enabled": str(settings.RECRUITER_WORKSPACE_V2_ENABLED).lower()}


def _policy_response(policy):
    return {"job_id": policy.job_id, "mode": policy.mode, "reveal_stage": policy.reveal_stage, "masked_fields": policy.masked_fields, "version": policy.version}


@router.get("/jobs/{job_id}/review-privacy")
async def read_review_privacy(job_id: str, db: AsyncSession = Depends(get_db)):
    return _policy_response(await get_review_privacy_policy(db, job_id))


@router.put("/jobs/{job_id}/review-privacy")
async def set_review_privacy(job_id: str, payload: ReviewPrivacyPolicyUpdate, if_match: str = Header(..., alias="If-Match"), x_actor_id: str = Header("system"), db: AsyncSession = Depends(get_db)):
    try:
        policy = await update_review_privacy_policy(db, job_id, payload.mode, payload.reveal_stage, int(if_match.strip('"')), x_actor_id)
        return _policy_response(policy)
    except RuntimeError as error:
        raise HTTPException(409, detail={"code": "VERSION_CONFLICT", "message": str(error)}) from error
    except ValueError as error:
        raise HTTPException(400, detail={"code": "INVALID_ETAG", "message": "If-Match phải là version chính sách."}) from error


from app.api.criteria import router as criteria_router  # noqa: E402
from app.api.upload_batches import router as upload_batches_router  # noqa: E402
from app.api.candidates import router as candidates_router  # noqa: E402
from app.api.recruiter_productivity import router as productivity_router  # noqa: E402
from app.api.decisions import router as decisions_router  # noqa: E402
from app.api.comparisons import router as comparisons_router  # noqa: E402
from app.api.recruiter_analytics import router as analytics_router  # noqa: E402

router.include_router(criteria_router)
router.include_router(upload_batches_router)
router.include_router(candidates_router)
router.include_router(productivity_router)
router.include_router(decisions_router)
router.include_router(comparisons_router)
router.include_router(analytics_router)
