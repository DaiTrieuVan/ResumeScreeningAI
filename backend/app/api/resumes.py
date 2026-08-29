from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.storage import save_uploaded_pdf
from app.services.pdf_parser import extract_text_from_pdf, extract_resume_metadata
from app.models.candidate_resume import CandidateResume
from app.schemas.candidate_resume import CandidateResumeResponse

router = APIRouter(prefix="/resumes", tags=["Candidate Resumes"])

@router.post("/upload", response_model=List[CandidateResumeResponse], status_code=status.HTTP_200_OK)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    saved_resumes = []
    for file in files:
        file_bytes = await file.read()
        file_size = len(file_bytes)
        await file.seek(0)
        
        unique_name, dest_path = await save_uploaded_pdf(file)
        
        parse_status = "SUCCESS"
        error_msg = None
        raw_text = ""
        meta = {"candidate_name": file.filename, "email": "", "phone": ""}
        
        try:
            raw_text = extract_text_from_pdf(dest_path)
            meta = extract_resume_metadata(raw_text)
        except Exception as e:
            parse_status = "FAILED"
            error_msg = str(e)
            
        resume = CandidateResume(
            job_id=job_id,
            file_name=file.filename or unique_name,
            file_path=dest_path,
            file_size_bytes=file_size,
            raw_text=raw_text,
            parsed_name=meta.get("candidate_name"),
            parsed_email=meta.get("email"),
            parsed_phone=meta.get("phone"),
            parse_status=parse_status,
            parse_error_message=error_msg
        )
        db.add(resume)
        saved_resumes.append(resume)
        
    await db.commit()
    for r in saved_resumes:
        await db.refresh(r)
        
    return saved_resumes

@router.get("", response_model=List[CandidateResumeResponse])
async def list_resumes(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CandidateResume).order_by(CandidateResume.uploaded_at.desc()))
    return result.scalars().all()
