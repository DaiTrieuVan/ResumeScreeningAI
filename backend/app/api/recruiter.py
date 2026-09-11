from fastapi import APIRouter


router = APIRouter(prefix="/recruiter", tags=["Recruiter Workspace"])


@router.get("/health")
async def recruiter_health() -> dict[str, str]:
    return {"status": "healthy", "workspace": "recruiter-v2"}


from app.api.criteria import router as criteria_router  # noqa: E402
from app.api.upload_batches import router as upload_batches_router  # noqa: E402

router.include_router(criteria_router)
router.include_router(upload_batches_router)
