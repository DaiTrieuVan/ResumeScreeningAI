# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.screening_result import ScreeningResult
from app.models.candidate_resume import CandidateResume
from app.models.job_posting import JobPosting
from app.services.reranker_service import detect_competition_honors
from app.core.exceptions import ResourceNotFoundException
from app.models.audit_event import AuditEvent
from app.services.candidate_privacy_service import require_candidate_access

router = APIRouter(prefix="/exports", tags=["Export Data"])

@router.get("/csv/{job_id}", response_class=Response)
async def export_shortlist_csv(
    job_id: str,
    status_filter: Optional[str] = "SHORTLISTED",
    x_actor_id: str = Header("system"),
    x_actor_role: str = Header("system"),
    db: AsyncSession = Depends(get_db)
):
    try:
        require_candidate_access(x_actor_role)
    except PermissionError as error:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": str(error)}) from error
    job_res = await db.execute(select(JobPosting).where(JobPosting.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise ResourceNotFoundException("JobPosting", job_id)

    stmt = (
        select(ScreeningResult, CandidateResume)
        .join(CandidateResume, ScreeningResult.resume_id == CandidateResume.id)
        .where(ScreeningResult.job_id == job_id)
        .order_by(
            ScreeningResult.overall_score.desc(),
            ScreeningResult.stage1_similarity_score.desc()
        )
    )
    res = await db.execute(stmt)
    all_rows = res.all()

    sf = (status_filter or "SHORTLISTED").upper()

    # Smart filtering logic
    if sf == "SHORTLISTED":
        # First check if explicit SHORTLISTED recruiter_status exists
        explicit = [r for r in all_rows if r[0].recruiter_status == "SHORTLISTED"]
        if explicit:
            rows = explicit
        else:
            # Fallback to Top candidates (overall_score >= 60.0 or top 50%)
            rows = [r for r in all_rows if (r[0].overall_score or 0) >= 60.0]
            if not rows and all_rows:
                rows = all_rows[: max(1, len(all_rows) // 2)]
    elif sf == "REJECTED":
        # Check if explicit REJECTED recruiter_status exists
        explicit = [r for r in all_rows if r[0].recruiter_status == "REJECTED"]
        if explicit:
            rows = explicit
        else:
            # Fallback to low-scoring candidates (overall_score < 60.0)
            rows = [r for r in all_rows if (r[0].overall_score or 0) < 60.0]
            if not rows and all_rows:
                rows = all_rows[max(1, len(all_rows) // 2):]
    else:
        rows = all_rows

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header with clear Vietnamese column labels
    writer.writerow([
        "Tên Ứng viên",
        "Email",
        "Điểm Phù hợp Tổng thể (%)",
        "Điểm Kỹ năng (%)",
        "Điểm Kinh nghiệm (%)",
        "Điểm Học vấn (%)",
        "Huy hiệu Thành tích / Giải thưởng",
        "Trạng thái Tuyển dụng",
        "Điểm mạnh Nổi bật",
        "Điểm thiếu sót / Cần bổ sung",
        "Giải trình Phân tích AI",
        "Ghi chú Tuyển dụng"
    ])

    for s_res, c_res in rows:
        badges = detect_competition_honors(c_res.raw_text or "")
        writer.writerow([
            c_res.parsed_name or c_res.file_name,
            c_res.parsed_email or "N/A",
            f"{s_res.overall_score:.1f}%",
            f"{s_res.skills_sub_score:.1f}%",
            f"{s_res.experience_sub_score:.1f}%",
            f"{s_res.education_sub_score:.1f}%",
            "; ".join(badges) if badges else "Không",
            s_res.recruiter_status,
            "; ".join(s_res.strengths_summary or []),
            "; ".join(s_res.gaps_summary or []),
            s_res.ai_reasoning or "",
            s_res.recruiter_feedback_notes or ""
        ])

    # Prepend UTF-8 BOM (\ufeff) so Microsoft Excel opens Vietnamese text perfectly without font errors
    csv_content = "\ufeff" + output.getvalue()
    clean_job_title = job.title.replace(' ', '_').replace('/', '_')
    filename = f"{sf.lower()}_{clean_job_title}.csv"

    db.add(AuditEvent(actor_id=x_actor_id, action="EXPORT_CANDIDATES_CSV", resource_type="JobPosting", resource_id=job.id, metadata_json={"status_filter": sf, "row_count": len(rows)}))

    return Response(
        content=csv_content.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
