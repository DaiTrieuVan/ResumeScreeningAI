"""
Demo: Trich xuat CV tu file PDF -> text -> goi Gemini API (cloud, mien phi)
de lay thong tin co cau truc (structured output) dang JSON.

Yeu cau truoc khi chay:
1. Lay API key mien phi tai: https://aistudio.google.com/apikey
2. Set bien moi truong GEMINI_API_KEY (hoac truyen qua --api-key)
   Windows PowerShell:  $env:GEMINI_API_KEY="dan_api_key_vao_day"
   macOS/Linux:         export GEMINI_API_KEY="dan_api_key_vao_day"
3. pip install google-genai pdfplumber pydantic

Cach chay:
    python cv_extract_gemini.py duong/dan/cv.pdf
    python cv_extract_gemini.py duong/dan/cv.pdf --model gemini-2.5-flash

Luu y ve du lieu:
Ban Gemini API mien phi cho phep Google dung du lieu ban gui de cai thien
model cua ho. Voi CV that cua nguoi dung that, can can nhac an danh hoa
truoc khi gui, hoac dung goi tra phi/Vertex AI neu can bao mat du lieu.
"""

import argparse
import json
import os
import re
import sys
from typing import List, Optional

import pdfplumber
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """Ban la he thong trich xuat thong tin CV.
QUY TAC BAT BUOC:
- Chi trich xuat thong tin CO TRONG van ban, khong suy doan hay bo sung.
- Neu mot truong khong co thong tin, de gia tri null (hoac mang rong neu la danh sach).
- KHONG bao gom tuoi, gioi tinh, tinh trang hon nhan, hoac mo ta ngoai hinh trong ket qua.
- Chuan hoa ten ky nang cong nghe ve dang pho bien nhat (vi du: "ReactJS" -> "React")."""


# --- Dinh nghia schema bang Pydantic: Gemini se bat buoc tra ve dung cau truc nay ---

class Education(BaseModel):
    degree: Optional[str] = Field(default=None, description="Bang cap, vi du: Dai hoc, Cao dang")
    major: Optional[str] = Field(default=None, description="Chuyen nganh")
    school: Optional[str] = Field(default=None, description="Ten truong")
    graduation_year: Optional[int] = Field(default=None, description="Nam tot nghiep")


class WorkExperience(BaseModel):
    position: Optional[str] = Field(default=None, description="Vi tri cong viec")
    company: Optional[str] = Field(default=None, description="Ten cong ty")
    duration: Optional[str] = Field(default=None, description="Thoi gian lam viec, vi du: 06/2024 - 12/2024")
    description: Optional[str] = Field(default=None, description="Mo ta cong viec, thanh tich")


class CVData(BaseModel):
    full_name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    education: List[Education] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Trich xuat text tho tu file PDF CV bang pdfplumber."""
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            chunks.append(page_text)
    return clean_text("\n".join(chunks))


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def call_gemini(cv_text: str, api_key: str, model: str = DEFAULT_MODEL) -> dict:
    """Goi Gemini API, ep tra ve JSON dung schema CVData bang response_schema."""
    client = genai.Client(api_key=api_key)

    prompt = f"""{SYSTEM_INSTRUCTION}

Noi dung CV can trich xuat:
---
{cv_text}
---"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CVData,
            temperature=0,  # giam tinh "sang tao", ket qua on dinh hon giua cac lan chay
        ),
    )
    return json.loads(response.text)


def main():
    parser = argparse.ArgumentParser(description="Trich xuat CV PDF thanh JSON bang Gemini API")
    parser.add_argument("pdf_path", help="Duong dan toi file CV PDF")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ten model Gemini (mac dinh: {DEFAULT_MODEL})")
    parser.add_argument("--api-key", default=None, help="Gemini API key (mac dinh doc tu bien moi truong GEMINI_API_KEY)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Loi] Chua co API key. Set bien moi truong GEMINI_API_KEY hoac truyen --api-key.", file=sys.stderr)
        print("      Lay API key mien phi tai: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)

    print(f"[1/3] Dang trich xuat text tu {args.pdf_path} ...")
    cv_text = extract_text_from_pdf(args.pdf_path)
    print(f"      -> Trich xuat duoc {len(cv_text)} ky tu.")

    if not cv_text.strip():
        print("[Canh bao] Khong trich xuat duoc text nao. CV co the la ban scan anh, can OCR (pytesseract).")
        sys.exit(1)

    print(f"[2/3] Dang goi Gemini API (model: {args.model}) ...")
    structured_data = call_gemini(cv_text, api_key=api_key, model=args.model)

    print("[3/3] Ket qua trich xuat co cau truc:")
    print(json.dumps(structured_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
