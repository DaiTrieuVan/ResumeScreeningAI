import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.screening_result import ScreeningResult
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.core.exceptions import ResourceNotFoundException

router = APIRouter(prefix="/exports", tags=["Export Data"])

@router.get("/csv/{job_id}", response_class=Response)
async def export_shortlist_csv(
    job_id: str,
    status_filter: Optional[str] = "SHORTLISTED",
    db: AsyncSession = Depends(get_db)
):
    job_res = await db.execute(select(JobPosting).where(JobPosting.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise ResourceNotFoundException("JobPosting", job_id)

    stmt = (
        select(ScreeningResult, CandidateResume)
        .join(CandidateResume, ScreeningResult.resume_id == CandidateResume.id)
        .where(ScreeningResult.job_id == job_id)
    )
    if status_filter and status_filter.upper() != "ALL":
        stmt = stmt.where(ScreeningResult.recruiter_status == status_filter.upper())

    stmt = stmt.order_by(ScreeningResult.overall_score.desc())
    res = await db.execute(stmt)
    rows = res.all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Candidate Name",
        "Email",
        "Overall Score (%)",
        "Skills Sub-score",
        "Experience Sub-score",
        "Education Sub-score",
        "Recruiter Status",
        "Key Strengths",
        "Identified Gaps",
        "AI Reasoning",
        "Recruiter Notes"
    ])

    for s_res, c_res in rows:
        writer.writerow([
            c_res.parsed_name or c_res.file_name,
            c_res.parsed_email or "N/A",
            f"{s_res.overall_score:.1f}",
            f"{s_res.skills_sub_score:.1f}",
            f"{s_res.experience_sub_score:.1f}",
            f"{s_res.education_sub_score:.1f}",
            s_res.recruiter_status,
            "; ".join(s_res.strengths_summary or []),
            "; ".join(s_res.gaps_summary or []),
            s_res.ai_reasoning or "",
            s_res.recruiter_feedback_notes or ""
        ])

    csv_content = output.getvalue()
    filename = f"shortlist_{job.title.replace(' ', '_')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
