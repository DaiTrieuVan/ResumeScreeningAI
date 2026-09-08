import re
import pdfplumber
from app.core.exceptions import ParsingException

def sanitize_extracted_text(text: str) -> str:
    """
    Cleans up extracted text, normalizing whitespace and removing invalid control chars while preserving Vietnamese diacritics.
    """
    if not text:
        return ""
    # Normalize unicode whitespace
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Remove control characters except standard readable space/letters
    text = re.sub(r'[^\w\s\.,;:!\?\-\(\)@\/\\#\%\&\$\+\=\<\>\[\]\{\}\'"àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text stream from a PDF file using PyMuPDF (fitz) for maximum speed (5-15ms),
    with pdfplumber as a fallback.
    """
    full_text = []
    
    # Primary: PyMuPDF (fitz) - High performance C engine
    try:
        import fitz
        doc = fitz.open(file_path)
        for page in doc:
            text = page.get_text()
            if text:
                full_text.append(text)
        doc.close()
        extracted = " ".join(full_text)
        sanitized = sanitize_extracted_text(extracted)
        if sanitized:
            return sanitized
    except Exception:
        pass  # Fallback to pdfplumber below

    # Fallback: pdfplumber
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(layout=False) or ""
                if page_text:
                    full_text.append(page_text)
        
        extracted = " ".join(full_text)
        sanitized = sanitize_extracted_text(extracted)
        
        if not sanitized:
            raise ParsingException(file_path, "PDF appears to be empty or contains no readable digital text.")
            
        return sanitized
    except ParsingException:
        raise
    except Exception as e:
        raise ParsingException(file_path, f"Failed to extract text from PDF: {str(e)}")

import zipfile
import io
import os
from typing import List, Tuple

def extract_pdfs_from_zip(zip_bytes_or_path) -> List[Tuple[str, bytes]]:
    """
    Extracts all PDF files from a ZIP archive.
    Returns a list of tuples: (filename, pdf_file_bytes)
    """
    pdf_files = []
    zip_obj = zipfile.ZipFile(io.BytesIO(zip_bytes_or_path) if isinstance(zip_bytes_or_path, bytes) else zip_bytes_or_path)
    
    for zip_info in zip_obj.infolist():
        if zip_info.is_dir():
            continue
        filename = os.path.basename(zip_info.filename)
        if filename.startswith('._') or filename.startswith('__MACOSX'):
            continue  # Ignore macOS metadata files
        if filename.lower().endswith('.pdf'):
            with zip_obj.open(zip_info) as f:
                pdf_files.append((filename, f.read()))
                
    return pdf_files

def extract_resume_metadata(raw_text: str) -> dict:
    """
    Basic regex extraction for Candidate Name, Email, and Phone prior to LLM parsing.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+?\d{1,4}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}'
    
    email_match = re.search(email_pattern, raw_text)
    phone_match = re.search(phone_pattern, raw_text)
    
    email = email_match.group(0) if email_match else ""
    phone = phone_match.group(0) if phone_match else ""
    
    # Simple heuristic for Candidate Name: first line or words before email/phone
    words = raw_text.split()
    name = " ".join(words[:3]) if words else "Unknown Candidate"
    
    return {
        "candidate_name": name,
        "email": email,
        "phone": phone
    }
