# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.storage import save_uploaded_pdf, delete_stored_file
from app.services.pdf_parser import extract_text_from_pdf
from app.services.gap_advisor_service import analyze_career_gap
from app.models.gap_analysis import GapAnalysis
from app.schemas.gap_analysis import GapAnalysisResponse, GapAnalysisRequest

router = APIRouter(prefix="/gap-advisor", tags=["Career Gap Advisor"])

@router.post("/analyze", response_model=GapAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_gap_endpoint(
    job_title: Optional[str] = Form(None),
    job_description: str = Form(...),
    cv_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    extracted_cv_text = cv_text or ""
    temp_path = None
    
    if file:
        _, temp_path = await save_uploaded_pdf(file)
        try:
            extracted_cv_text = extract_text_from_pdf(temp_path)
        finally:
            delete_stored_file(temp_path)

    analysis_data = await analyze_career_gap(
        job_title=job_title or "Target Role",
        job_description=job_description,
        cv_text=extracted_cv_text
    )

    record = GapAnalysis(
        target_job_title=job_title,
        target_job_description=job_description,
        overall_score=analysis_data.get("overall_score", 7.5),
        score_label=analysis_data.get("score_label", "Tốt"),
        category_scores=analysis_data.get("category_scores") or {},
        strengths=analysis_data.get("strengths") or [],
        weaknesses=analysis_data.get("weaknesses") or [],
        spelling_and_format_errors=analysis_data.get("spelling_and_format_errors") or [],
        matched_skills=analysis_data.get("matched_skills") or [],
        missing_skills=analysis_data.get("missing_skills") or [],
        suggested_action_items=analysis_data.get("suggested_action_items") or [],
        summary_explanation=analysis_data.get("summary_explanation") or ""
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return GapAnalysisResponse(
        id=record.id,
        target_job_title=record.target_job_title,
        overall_score=record.overall_score or 7.5,
        score_label=record.score_label or "Tốt",
        category_scores=record.category_scores or {},
        strengths=record.strengths or [],
        weaknesses=record.weaknesses or [],
        spelling_and_format_errors=record.spelling_and_format_errors or [],
        matched_skills=record.matched_skills or [],
        missing_skills=record.missing_skills or [],
        suggested_action_items=record.suggested_action_items or [],
        summary_explanation=record.summary_explanation or "",
        created_at=record.created_at
    )
