import json
import asyncio
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel

from app.core.database import get_db, AsyncSessionLocal
from app.models.job_posting import JobPosting
from app.models.candidate_resume import CandidateResume
from app.models.screening_result import ScreeningResult
from app.services.embedding_service import rank_candidates_by_vector_similarity
from app.services.reranker_service import rerank_candidate_resume
from app.core.exceptions import ResourceNotFoundException

logger = logging.getLogger(__name__)

# --- Pipeline Optimization Constants ---
# Top-K: Only send candidates with Stage1 score >= threshold to expensive LLM.
# Candidates below threshold get heuristic-only scores.
TOP_K_SIMILARITY_THRESHOLD = 25.0  # Minimum vector similarity % to qualify for LLM
TOP_K_MAX_CANDIDATES = 80          # Maximum number of candidates sent to LLM
# Concurrent LLM: Number of parallel Gemini API calls via asyncio.Semaphore
LLM_CONCURRENCY_LIMIT = 5

router = APIRouter(prefix="/screenings", tags=["Screening & Evaluation"])

class EvaluateRequest(BaseModel):
    job_id: str
    resume_ids: Optional[List[str]] = None

async def get_resumes_for_job(job_id: str, resume_ids: Optional[List[str]], db: AsyncSession) -> List[CandidateResume]:
    if resume_ids:
        res_stmt = select(CandidateResume).where(
            CandidateResume.parse_status == "SUCCESS",
            CandidateResume.id.in_(resume_ids)
        )
        res = await db.execute(res_stmt)
        return res.scalars().all()

    # 1. First attempt: fetch resumes explicitly uploaded for this job_id
    job_stmt = select(CandidateResume).where(
        CandidateResume.parse_status == "SUCCESS",
        CandidateResume.job_id == job_id
    )
    job_resumes = (await db.execute(job_stmt)).scalars().all()
    if job_resumes:
        return job_resumes

    # 2. Fallback: if no resumes linked to job_id exist, fetch unlinked legacy resumes
    legacy_stmt = select(CandidateResume).where(
        CandidateResume.parse_status == "SUCCESS",
        CandidateResume.job_id == None
    )
    return (await db.execute(legacy_stmt)).scalars().all()

class ScreeningResultResponse(BaseModel):
    id: str
    job_id: str
    resume_id: str
    stage1_similarity_score: float
    skills_sub_score: float
    experience_sub_score: float
    education_sub_score: float
    overall_score: float
    skills_summary: Optional[str] = None
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    strengths_summary: List[str]
    gaps_summary: List[str]
    ai_reasoning: str
    recruiter_status: str
    recruiter_feedback_notes: Optional[str] = None
    score_override: Optional[float] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_file_name: Optional[str] = None

@router.post("/evaluate", response_model=List[ScreeningResultResponse])
async def evaluate_screening(
    req: EvaluateRequest,
    db: AsyncSession = Depends(get_db)
):
    # Fetch job posting
    job_res = await db.execute(select(JobPosting).where(JobPosting.id == req.job_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise ResourceNotFoundException("JobPosting", req.job_id)

    # Fetch candidate resumes prioritizing job_id linked resumes
    resumes = await get_resumes_for_job(req.job_id, req.resume_ids, db)

    if not resumes:
        return []

    # Build job requirement string for vector similarity
    jd_text = f"Job Title: {job.title}. Required Skills: {', '.join(job.required_skills or [])}. Department: {job.department or ''}"
    resume_tuples = [(r.id, r.raw_text or "") for r in resumes]

    # Stage 1: Fast Embedding Pre-ranking
    stage1_rankings = dict(rank_candidates_by_vector_similarity(jd_text, resume_tuples))

    results = []
    for r in resumes:
        sim_score = stage1_rankings.get(r.id, 50.0)

        # Stage 2: Detailed LLM Reranking
        eval_data = await rerank_candidate_resume(
            job_title=job.title,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
            min_experience=job.min_years_experience or 0,
            required_education=job.required_education or "",
            resume_text=r.raw_text or ""
        )

        # Update candidate parsed metadata if found by LLM
        if eval_data.get("candidate_name") and eval_data["candidate_name"] != "Unknown Candidate":
            r.parsed_name = eval_data["candidate_name"]
        if eval_data.get("email"):
            r.parsed_email = eval_data["email"]

        # Calculate overall weighted score client/API side
        s_score = eval_data["skills_sub_score"]
        e_score = eval_data["experience_sub_score"]
        ed_score = eval_data["education_sub_score"]
        overall = round(
            (s_score * job.weight_skills) +
            (e_score * job.weight_experience) +
            (ed_score * job.weight_education),
            1
        )

        # Check existing result or create new
        existing_res = await db.execute(
            select(ScreeningResult).where(
                and_(ScreeningResult.job_id == job.id, ScreeningResult.resume_id == r.id)
            )
        )
        s_result = existing_res.scalar_one_or_none()

        if not s_result:
            s_result = ScreeningResult(
                job_id=job.id,
                resume_id=r.id
            )
            db.add(s_result)

        s_result.stage1_similarity_score = sim_score
        s_result.skills_sub_score = s_score
        s_result.experience_sub_score = e_score
        s_result.education_sub_score = ed_score
        s_result.overall_score = overall
        s_result.skills_summary = eval_data.get("skills_summary") or ""
        s_result.experience_summary = eval_data.get("experience_summary") or ""
        s_result.education_summary = eval_data.get("education_summary") or ""
        s_result.strengths_summary = eval_data["strengths_summary"]
        s_result.gaps_summary = eval_data["gaps_summary"]
        s_result.ai_reasoning = eval_data["ai_reasoning"]

    await db.commit()

    # Query returned results with candidate details
    return await fetch_screenings_for_job(job.id, db)

@router.post("/evaluate/stream")
async def evaluate_screening_stream(req: EvaluateRequest):
    async def event_generator():
        async with AsyncSessionLocal() as db:
            job_res = await db.execute(select(JobPosting).where(JobPosting.id == req.job_id))
            job = job_res.scalar_one_or_none()
            if not job:
                yield f"data: {json.dumps({'stage': 'error', 'message': f'Vị trí tuyển dụng {req.job_id} không tồn tại'})}\n\n"
                return

            resumes = await get_resumes_for_job(req.job_id, req.resume_ids, db)

            if not resumes:
                yield f"data: {json.dumps({'stage': 'completed', 'progress_percent': 100, 'total': 0, 'current': 0, 'results': []})}\n\n"
                return

            total_resumes = len(resumes)
            yield f"data: {json.dumps({'stage': 'stage1_vector', 'progress_percent': 5, 'total': total_resumes, 'current': 0, 'message': f'Đang khởi động khớp nối Vector Similarity cho {total_resumes} ứng viên...'})}\n\n"

            jd_text = f"Job Title: {job.title}. Required Skills: {', '.join(job.required_skills or [])}. Department: {job.department or ''}"
            resume_tuples = [(r.id, r.raw_text or "") for r in resumes]

            stage1_rankings = dict(rank_candidates_by_vector_similarity(jd_text, resume_tuples))

            yield f"data: {json.dumps({'stage': 'stage1_vector_done', 'progress_percent': 15, 'total': total_resumes, 'current': 0, 'message': 'Đã hoàn thành khớp nối Vector. Bắt đầu đánh giá chuyên sâu AI (LLM Reranking)...'})}\n\n"

            for idx, r in enumerate(resumes, start=1):
                cand_name = r.parsed_name or r.file_name or f"Ứng viên #{idx}"
                pct = round(15 + (idx / total_resumes) * 80)
                
                yield f"data: {json.dumps({'stage': 'stage2_llm', 'progress_percent': pct, 'total': total_resumes, 'current': idx, 'current_candidate': cand_name, 'message': f'Đang phân tích AI cho ứng viên ({idx}/{total_resumes}): {cand_name}'})}\n\n"

                sim_score = stage1_rankings.get(r.id, 50.0)

                eval_data = await rerank_candidate_resume(
                    job_title=job.title,
                    required_skills=job.required_skills or [],
                    preferred_skills=job.preferred_skills or [],
                    min_experience=job.min_years_experience or 0,
                    required_education=job.required_education or "",
                    resume_text=r.raw_text or ""
                )

                if eval_data.get("candidate_name") and eval_data["candidate_name"] != "Unknown Candidate":
                    r.parsed_name = eval_data["candidate_name"]
                if eval_data.get("email"):
                    r.parsed_email = eval_data["email"]

                s_score = eval_data["skills_sub_score"]
                e_score = eval_data["experience_sub_score"]
                ed_score = eval_data["education_sub_score"]
                overall = round(
                    (s_score * job.weight_skills) +
                    (e_score * job.weight_experience) +
                    (ed_score * job.weight_education),
                    1
                )

                existing_res = await db.execute(
                    select(ScreeningResult).where(
                        and_(ScreeningResult.job_id == job.id, ScreeningResult.resume_id == r.id)
                    )
                )
                s_result = existing_res.scalar_one_or_none()

                if not s_result:
                    s_result = ScreeningResult(job_id=job.id, resume_id=r.id)
                    db.add(s_result)

                s_result.stage1_similarity_score = sim_score
                s_result.skills_sub_score = s_score
                s_result.experience_sub_score = e_score
                s_result.education_sub_score = ed_score
                s_result.overall_score = overall
                s_result.skills_summary = eval_data.get("skills_summary") or ""
                s_result.experience_summary = eval_data.get("experience_summary") or ""
                s_result.education_summary = eval_data.get("education_summary") or ""
                s_result.strengths_summary = eval_data["strengths_summary"]
                s_result.gaps_summary = eval_data["gaps_summary"]
                s_result.ai_reasoning = eval_data["ai_reasoning"]

                await db.commit()

            final_results = await fetch_screenings_for_job(job.id, db)
            results_data = [item.model_dump() for item in final_results]
            
            yield f"data: {json.dumps({'stage': 'completed', 'progress_percent': 100, 'total': total_resumes, 'current': total_resumes, 'message': 'Đã hoàn tất phân tích toàn bộ CV!', 'results': results_data})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def fetch_screenings_for_job(job_id: str, db: AsyncSession) -> List[ScreeningResultResponse]:
    stmt = (
        select(ScreeningResult, CandidateResume)
        .join(CandidateResume, ScreeningResult.resume_id == CandidateResume.id)
        .where(ScreeningResult.job_id == job_id)
        .order_by(ScreeningResult.overall_score.desc())
    )
    res = await db.execute(stmt)
    rows = res.all()

    out = []
    for s_res, c_res in rows:
        out.append(ScreeningResultResponse(
            id=s_res.id,
            job_id=s_res.job_id,
            resume_id=s_res.resume_id,
            stage1_similarity_score=s_res.stage1_similarity_score or 0.0,
            skills_sub_score=s_res.skills_sub_score or 0.0,
            experience_sub_score=s_res.experience_sub_score or 0.0,
            education_sub_score=s_res.education_sub_score or 0.0,
            overall_score=s_res.overall_score or 0.0,
            skills_summary=getattr(s_res, 'skills_summary', None),
            experience_summary=getattr(s_res, 'experience_summary', None),
            education_summary=getattr(s_res, 'education_summary', None),
            strengths_summary=s_res.strengths_summary or [],
            gaps_summary=s_res.gaps_summary or [],
            ai_reasoning=s_res.ai_reasoning or "",
            recruiter_status=s_res.recruiter_status or "NEW",
            recruiter_feedback_notes=s_res.recruiter_feedback_notes,
            score_override=s_res.score_override,
            candidate_name=c_res.parsed_name or c_res.file_name,
            candidate_email=c_res.parsed_email,
            candidate_file_name=c_res.file_name
        ))
    return out

@router.get("/{job_id}", response_model=List[ScreeningResultResponse])
async def get_job_screenings(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await fetch_screenings_for_job(job_id, db)

from app.schemas.screening_result import RecruiterStatusUpdate

@router.patch("/{screening_id}/status", response_model=ScreeningResultResponse)
async def update_screening_status(
    screening_id: str,
    update_in: RecruiterStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(ScreeningResult).where(ScreeningResult.id == screening_id))
    s_result = res.scalar_one_or_none()
    if not s_result:
        raise ResourceNotFoundException("ScreeningResult", screening_id)
        
    s_result.recruiter_status = update_in.recruiter_status
    if update_in.recruiter_feedback_notes is not None:
        s_result.recruiter_feedback_notes = update_in.recruiter_feedback_notes
    if update_in.score_override is not None:
        s_result.score_override = update_in.score_override
        s_result.overall_score = update_in.score_override
        
    await db.commit()
    await db.refresh(s_result)
    
    # Return with candidate metadata
    c_res = await db.execute(select(CandidateResume).where(CandidateResume.id == s_result.resume_id))
    resume = c_res.scalar_one()
    
    return ScreeningResultResponse(
        id=s_result.id,
        job_id=s_result.job_id,
        resume_id=s_result.resume_id,
        stage1_similarity_score=s_result.stage1_similarity_score or 0.0,
        skills_sub_score=s_result.skills_sub_score or 0.0,
        experience_sub_score=s_result.experience_sub_score or 0.0,
        education_sub_score=s_result.education_sub_score or 0.0,
        overall_score=s_result.overall_score or 0.0,
        skills_summary=getattr(s_result, 'skills_summary', None),
        experience_summary=getattr(s_result, 'experience_summary', None),
        education_summary=getattr(s_result, 'education_summary', None),
        strengths_summary=s_result.strengths_summary or [],
        gaps_summary=s_result.gaps_summary or [],
        ai_reasoning=s_result.ai_reasoning or "",
        recruiter_status=s_result.recruiter_status or "NEW",
        recruiter_feedback_notes=s_result.recruiter_feedback_notes,
        score_override=s_result.score_override,
        candidate_name=resume.parsed_name or resume.file_name,
        candidate_email=resume.parsed_email,
        candidate_file_name=resume.file_name
    )

