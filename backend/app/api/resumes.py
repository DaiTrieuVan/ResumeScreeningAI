# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import os
import io
import uuid
import aiofiles
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.storage import save_uploaded_pdf
from app.services.pdf_parser import extract_text_from_pdf, extract_resume_metadata, extract_pdfs_from_zip
from app.services.embedding_service import get_text_embedding, serialize_embedding
from app.models.candidate_resume import CandidateResume
from app.schemas.candidate_resume import CandidateResumeResponse

router = APIRouter(prefix="/resumes", tags=["Candidate Resumes"])

async def process_single_pdf(
    filename: str,
    file_bytes: bytes,
    job_id: Optional[str],
    db: AsyncSession
) -> CandidateResume:
    """Helper to save, parse PDF text, compute vector embedding and add to session."""
    # Ensure storage dir exists
    storage_dir = settings.STORAGE_DIR
    os.makedirs(storage_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    dest_path = os.path.join(storage_dir, unique_name)

    async with aiofiles.open(dest_path, "wb") as out_file:
        await out_file.write(file_bytes)

    parse_status = "SUCCESS"
    error_msg = None
    raw_text = ""
    meta = {"candidate_name": filename, "email": "", "phone": ""}
    emb_json = None

    try:
        raw_text = extract_text_from_pdf(dest_path)
        meta = extract_resume_metadata(raw_text)
        if raw_text:
            vec = get_text_embedding(raw_text)
            emb_json = serialize_embedding(vec)
    except Exception as e:
        parse_status = "FAILED"
        error_msg = str(e)

    resume = CandidateResume(
        job_id=job_id,
        file_name=filename,
        file_path=dest_path,
        file_size_bytes=len(file_bytes),
        raw_text=raw_text,
        parsed_name=meta.get("candidate_name"),
        parsed_email=meta.get("email"),
        parsed_phone=meta.get("phone"),
        parse_status=parse_status,
        parse_error_message=error_msg,
        embedding_json=emb_json
    )
    db.add(resume)
    return resume

@router.post("/upload", response_model=List[CandidateResumeResponse], status_code=status.HTTP_200_OK)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    saved_resumes = []
    for file in files:
        file_bytes = await file.read()
        if file.filename and file.filename.lower().endswith(".zip"):
            extracted_pdfs = extract_pdfs_from_zip(file_bytes)
            for fname, pbytes in extracted_pdfs:
                res = await process_single_pdf(fname, pbytes, job_id, db)
                saved_resumes.append(res)
        else:
            res = await process_single_pdf(file.filename or "resume.pdf", file_bytes, job_id, db)
            saved_resumes.append(res)

    await db.commit()
    for r in saved_resumes:
        await db.refresh(r)

    return saved_resumes

@router.post("/bulk-upload", response_model=List[CandidateResumeResponse], status_code=status.HTTP_200_OK)
async def bulk_upload_resumes(
    files: List[UploadFile] = File(...),
    job_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk upload endpoint: Accepts ZIP archives or multiple PDF files.
    """
    return await upload_resumes(files=files, job_id=job_id, db=db)

@router.get("", response_model=List[CandidateResumeResponse])
async def list_resumes(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CandidateResume).order_by(CandidateResume.uploaded_at.desc()))
    return result.scalars().all()
