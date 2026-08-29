from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.storage import save_uploaded_pdf, delete_stored_file
from app.services.pdf_parser import extract_text_from_pdf
from app.services.job_aggregator import seed_real_jobs_if_empty
from app.services.job_crawler_service import crawl_and_sync_jobs
from app.services.cv_job_matcher import match_cv_against_real_jobs
from app.models.real_job import RealJobPosting
from app.schemas.real_job import RealJobPostingResponse, CandidateJobMatchResponse

router = APIRouter(prefix="/real-jobs", tags=["Real Jobs & AI Matcher"])

@router.get("", response_model=List[RealJobPostingResponse])
async def list_real_jobs(
    location_tag: Optional[str] = None,
    min_salary: Optional[int] = None,
    skill: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    await seed_real_jobs_if_empty(db)
    
    query = select(RealJobPosting).where(RealJobPosting.status == "ACTIVE")
    if location_tag and location_tag.upper() != "ALL":
        query = query.where(RealJobPosting.location_tag == location_tag.upper())
    if min_salary and min_salary > 0:
        query = query.where(RealJobPosting.salary_max_vnd >= min_salary)

    res = await db.execute(query.order_by(RealJobPosting.created_at.desc()))
    jobs = res.scalars().all()

    if skill and skill.strip():
        search_skill = skill.lower()
        jobs = [j for j in jobs if any(search_skill in s.lower() for s in j.required_skills)]

    return jobs

@router.post("/match", response_model=List[CandidateJobMatchResponse])
async def match_cv_with_real_jobs(
    file: Optional[UploadFile] = File(None),
    cv_text: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    await seed_real_jobs_if_empty(db)

    extracted_text = cv_text or ""
    if file:
        _, temp_path = await save_uploaded_pdf(file)
        try:
            extracted_text = extract_text_from_pdf(temp_path)
        finally:
            delete_stored_file(temp_path)

    res = await db.execute(select(RealJobPosting).where(RealJobPosting.status == "ACTIVE"))
    jobs = res.scalars().all()

    job_dicts = []
    for j in jobs:
        job_dicts.append({
            "id": j.id,
            "source": j.source,
            "external_id": j.external_id,
            "title": j.title,
            "company_name": j.company_name,
            "company_logo_url": j.company_logo_url,
            "location": j.location,
            "location_tag": j.location_tag,
            "salary_text": j.salary_text,
            "salary_min_vnd": j.salary_min_vnd,
            "salary_max_vnd": j.salary_max_vnd,
            "required_skills": j.required_skills or [],
            "experience_required": j.experience_required,
            "description_text": j.description_text,
            "source_url": j.source_url,
            "status": j.status,
            "created_at": j.created_at
        })

    matched_list = await match_cv_against_real_jobs(extracted_text, job_dicts)

    out = []
    for idx, item in enumerate(matched_list):
        j_data = item["real_job"]
        out.append(CandidateJobMatchResponse(
            id=f"match-{idx}",
            real_job=RealJobPostingResponse(**j_data),
            match_score=item["match_score"],
            skills_sub_score=item["skills_sub_score"],
            experience_sub_score=item["experience_sub_score"],
            strengths_summary=item["strengths_summary"],
            gaps_summary=item["gaps_summary"],
            match_reasoning=item["match_reasoning"],
            saved_status="DEFAULT",
            evaluated_at=j_data["created_at"]
        ))

    return out

@router.post("/sync")
async def sync_real_jobs(db: AsyncSession = Depends(get_db)):
    count = await seed_real_jobs_if_empty(db)
    return {"status": "success", "synced_jobs_count": count}

@router.post("/crawl")
async def crawl_real_jobs(
    limit: int = 10, 
    target_urls: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    new_added, updated, total_active = await crawl_and_sync_jobs(db, limit=limit, target_urls=target_urls)
    return {
        "status": "success",
        "message": f"Đã cào dữ liệu thành công. Thêm mới: {new_added}, Cập nhật: {updated}.",
        "new_jobs_added": new_added,
        "existing_jobs_updated": updated,
        "total_active_jobs": total_active
    }

