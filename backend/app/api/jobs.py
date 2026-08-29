from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.job_posting import JobPosting
from app.schemas.job_posting import JobPostingCreate, JobPostingUpdate, JobPostingResponse
from app.core.exceptions import ResourceNotFoundException

router = APIRouter(prefix="/jobs", tags=["Job Postings"])

@router.post("", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
async def create_job_posting(
    job_in: JobPostingCreate,
    db: AsyncSession = Depends(get_db)
):
    job = JobPosting(**job_in.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

@router.get("", response_model=List[JobPostingResponse])
async def list_job_postings(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(JobPosting).order_by(JobPosting.created_at.desc()))
    return result.scalars().all()

@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job_posting(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(JobPosting).where(JobPosting.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ResourceNotFoundException("JobPosting", job_id)
    return job

@router.put("/{job_id}", response_model=JobPostingResponse)
async def update_job_posting(
    job_id: str,
    job_in: JobPostingUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(JobPosting).where(JobPosting.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ResourceNotFoundException("JobPosting", job_id)

    update_data = job_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(job, field, val)

    await db.commit()
    await db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_posting(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(JobPosting).where(JobPosting.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ResourceNotFoundException("JobPosting", job_id)

    await db.delete(job)
    await db.commit()
    return None
