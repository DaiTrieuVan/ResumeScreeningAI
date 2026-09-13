from statistics import median

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_evaluation import CandidateApplication
from app.models.upload_batch import UploadBatch


async def get_recruiter_analytics(db: AsyncSession, job_id: str):
    funnel_rows = (await db.execute(select(CandidateApplication.pipeline_stage, func.count(CandidateApplication.id)).where(CandidateApplication.job_id == job_id).group_by(CandidateApplication.pipeline_stage))).all()
    applications = (await db.scalars(select(CandidateApplication).where(CandidateApplication.job_id == job_id))).all()
    batches = (await db.scalars(select(UploadBatch).where(UploadBatch.job_id == job_id))).all()
    durations = [(batch.completed_at - batch.created_at).total_seconds() for batch in batches if batch.completed_at]
    decided = [application for application in applications if application.human_decision]
    overrides = sum(1 for application in decided if application.human_decision != application.ai_recommendation)
    return {
        "funnel": {stage: count for stage, count in funnel_rows},
        "upload_counts": {
            "total": sum(batch.total_count for batch in batches),
            "success": sum(batch.success_count for batch in batches),
            "failed": sum(batch.failed_count for batch in batches),
            "duplicate": sum(batch.duplicate_count for batch in batches),
        },
        "median_processing_seconds": round(median(durations), 2) if durations else 0,
        "ai_override_rate": overrides / len(decided) if decided else 0,
        "decided_count": len(decided),
    }
