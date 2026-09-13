# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import os
import uuid
import aiofiles
from fastapi import UploadFile
from app.core.config import settings

async def save_uploaded_pdf(file: UploadFile) -> tuple[str, str]:
    """
    Saves uploaded file into storage directory.
    Returns tuple of (unique_filename, absolute_file_path).
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext != ".pdf":
        ext = ".pdf"
    
    unique_filename = f"{uuid.uuid4()}{ext}"
    dest_path = os.path.join(settings.STORAGE_DIR, unique_filename)
    
    async with aiofiles.open(dest_path, "wb") as out_file:
        while content := await file.read(1024 * 1024):
            await out_file.write(content)
            
    return unique_filename, dest_path

def delete_stored_file(file_path: str) -> bool:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False
    return False
