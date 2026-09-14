# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import AppException, app_exception_handler
from app.api import jobs, resumes, screenings, gap_advisor, exports, real_jobs, recruiter, evaluations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    await init_db()
    from app.services.upload_batch_service import process_upload_batch
    from app.services.upload_recovery_service import reconcile_all_interrupted_items
    resumed = await reconcile_all_interrupted_items()
    for batch_id, item_ids in resumed.items():
        asyncio.create_task(process_upload_batch(batch_id, item_ids))
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# Include Routers
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(resumes.router, prefix=settings.API_V1_STR)
app.include_router(screenings.router, prefix=settings.API_V1_STR)
app.include_router(gap_advisor.router, prefix=settings.API_V1_STR)
app.include_router(exports.router, prefix=settings.API_V1_STR)
app.include_router(real_jobs.router, prefix=settings.API_V1_STR)
app.include_router(recruiter.router, prefix=settings.API_V1_STR)
app.include_router(evaluations.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}


@app.get(f"{settings.API_V1_STR}/runtime-status")
async def runtime_status():
    offline = settings.OFFLINE_MODE
    embedding_disabled = offline or not bool(settings.DEFAULT_EMBEDDING_MODEL)
    return {
        "mode": "offline" if offline else "online-capable",
        "fallback": offline or embedding_disabled or not bool(settings.GEMINI_API_KEY),
        "engine": settings.OFFLINE_ENGINE if offline else (settings.DEFAULT_LLM_MODEL if settings.GEMINI_API_KEY else settings.OFFLINE_ENGINE),
        "external_services": not offline,
    }
