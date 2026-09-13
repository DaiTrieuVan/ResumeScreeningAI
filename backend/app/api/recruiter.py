from fastapi import APIRouter
from app.core.config import settings


router = APIRouter(prefix="/recruiter", tags=["Recruiter Workspace"])


@router.get("/health")
async def recruiter_health() -> dict[str, str]:
    return {"status": "healthy", "workspace": "recruiter-v2", "enabled": str(settings.RECRUITER_WORKSPACE_V2_ENABLED).lower()}


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
