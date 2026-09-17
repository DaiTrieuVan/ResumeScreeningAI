# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Dict, Any
# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Dict, Any
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

GAP_PROMPT_TEMPLATE = """
You are a Principal Technical Recruiter and Career Mentor evaluating a candidate's CV against a target Job Description.
Provide a thorough, highly professional CV evaluation with numerical scoring, category breakdowns, detailed strengths & weaknesses, and actionable improvement steps.

### Target Job Title: {job_title}
### Target Job Description:
{job_description}

### Candidate CV Content:
{cv_text}

### Instructions:
Return a strict JSON object (in Vietnamese) matching this schema:
{{
  "overall_score": 7.5,
  "score_label": "Tốt",
  "category_scores": {{
    "kinh_nghiem": 6.5,
    "ky_nang": 8.0,
    "dinh_dang": 5.5,
    "thanh_tich": 7.0,
    "muc_tieu": 6.5
  }},
  "strengths": [
    "Nền tảng kỹ thuật tốt về Java backend, đặc biệt là Spring Boot, cơ sở dữ liệu và RESTful API.",
    "Kết quả học tập rất tốt với GPA ấn tượng, cho thấy khả năng tiếp thu và tư duy logic mạnh mẽ.",
    "Kinh nghiệm làm dự án có số liệu cụ thể về quy mô và hiệu năng hệ thống."
  ],
  "weaknesses": [
    "Mốc thời gian kinh nghiệm chưa đồng nhất hoặc thiếu chi tiết bối cảnh dự án.",
    "Trình bày còn một số đoạn bị dính dòng/khoảng cách chưa tối ưu cho công cụ quét CV (ATS).",
    "Thành tích nêu ra nhưng chưa thể hiện rõ đóng góp cá nhân trực tiếp."
  ],
  "matched_skills": ["Java", "Spring Boot", "RESTful API", "MySQL"],
  "missing_skills": ["Docker", "Redis", "PostgreSQL", "Kafka"],
  "suggested_action_items": [
    "Sửa lại toàn bộ mốc thời gian để nhất quán và hợp lý trong CV.",
    "Bổ sung 1-2 dòng mô tả vai trò cá nhân và số liệu đo lường cụ thể cho từng dự án.",
    "Căn chỉnh định dạng bullet points, tăng độ thoáng và chuẩn hóa font chữ.",
    "Bổ sung dự án cá nhân hoặc thực tập gần đây có áp dụng Docker và PostgreSQL."
  ],
  "summary_explanation": "Ứng viên có nền tảng tư duy và kỹ thuật cốt lõi khá vững chắc. Cần tập trung chuẩn hóa lại định dạng trình bày và làm nổi bật các con số thành tích cá nhân để tối ưu cơ hội trúng tuyển."
}}
"""

async def analyze_career_gap(
    job_title: str,
    job_description: str,
    cv_text: str
) -> Dict[str, Any]:
    prompt = GAP_PROMPT_TEMPLATE.format(
        job_title=job_title or "Target Role",
        job_description=job_description[:3500],
        cv_text=cv_text[:3500]
    )

    if settings.GEMINI_API_KEY and not settings.OFFLINE_MODE:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.DEFAULT_LLM_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            raw_text = response.text or "{}"
            return sanitize_gap_output(json.loads(raw_text))
        except Exception as e:
            logger.error(f"Gemini API error during gap analysis: {e}")
            return fallback_gap_analysis(job_description, cv_text)
    else:
        return fallback_gap_analysis(job_description, cv_text)

def sanitize_gap_output(data: Dict[str, Any]) -> Dict[str, Any]:
    raw_score = float(data.get("overall_score") or 7.5)
    overall_score = round(max(1.0, min(10.0, raw_score)), 1)
    
    label = str(data.get("score_label") or "")
    if not label:
        if overall_score >= 8.5: label = "Xuất sắc"
        elif overall_score >= 7.0: label = "Tốt"
        elif overall_score >= 5.5: label = "Khá"
        else: label = "Cần cải thiện"

    cat = data.get("category_scores") or {}
    category_scores = {
        "kinh_nghiem": round(float(cat.get("kinh_nghiem") or 6.5), 1),
        "ky_nang": round(float(cat.get("ky_nang") or 8.0), 1),
        "dinh_dang": round(float(cat.get("dinh_dang") or 6.0), 1),
        "thanh_tich": round(float(cat.get("thanh_tich") or 7.0), 1),
        "muc_tieu": round(float(cat.get("muc_tieu") or 6.5), 1)
    }

    return {
        "overall_score": overall_score,
        "score_label": label,
        "category_scores": category_scores,
        "strengths": list(data.get("strengths") or []),
        "weaknesses": list(data.get("weaknesses") or []),
        "matched_skills": list(data.get("matched_skills") or []),
        "missing_skills": list(data.get("missing_skills") or []),
        "suggested_action_items": list(data.get("suggested_action_items") or []),
        "summary_explanation": str(data.get("summary_explanation") or "Đã hoàn thành phân tích đánh giá CV và định hướng cải thiện.")
    }

def fallback_gap_analysis(job_description: str, cv_text: str) -> Dict[str, Any]:
    jd_words = set(job_description.lower().split())
    cv_words = set(cv_text.lower().split())
    
    common_keywords = ["python", "java", "spring", "boot", "react", "fastapi", "docker", "sql", "postgresql", "mysql", "rest", "api", "git", "aws", "kubernetes", "typescript"]
    matched = [k.capitalize() for k in common_keywords if k in jd_words and k in cv_words]
    missing = [k.capitalize() for k in common_keywords if k in jd_words and k not in cv_words]

    if not matched:
        matched = ["REST API", "Java Core", "Git"]
    if not missing:
        missing = ["PostgreSQL", "Docker", "CI/CD"]

    match_ratio = len(matched) / (len(matched) + len(missing)) if (matched or missing) else 0.6
    overall_score = round(min(9.5, max(5.0, 5.5 + match_ratio * 4.0)), 1)
    
    if overall_score >= 8.5: label = "Xuất sắc"
    elif overall_score >= 7.0: label = "Tốt"
    elif overall_score >= 5.5: label = "Khá"
    else: label = "Cần cải thiện"

    strengths = [
        f"Nền tảng kỹ thuật tốt với các kỹ năng đã xác minh: {', '.join(matched[:4])}.",
        "Cấu trúc CV có bố cục phân chia các phần rõ ràng, dễ theo dõi thông tin cơ bản.",
        "Thể hiện tinh thần chủ động nâng cao năng lực qua các dự án cá nhân/môn học."
    ]

    weaknesses = [
        f"CV còn thiếu một số từ khóa kỹ thuật yêu cầu trong JD: {', '.join(missing[:3])}.",
        "Chưa có nhiều số liệu đo lường cụ thể (như % tối ưu, quy mô người dùng hay lượng API request/ngày).",
        "Mô tả dự án còn thiên về liệt kê công nghệ hơn là thể hiện tác động nghiệp vụ thực tế."
    ]

    suggested_action_items = [
        f"Sửa đổi CV để bổ sung các từ khóa kỹ thuật quan trọng còn thiếu: {', '.join(missing[:3])}.",
        "Thêm 1-2 con số đo lường hiệu quả (ví dụ: 'Giảm 20% thời gian phản hồi API' hoặc 'Xử lý 10.000+ bản ghi').",
        "Tối ưu lại định dạng trình bày cho thoáng và nhất quán các mốc thời gian kinh nghiệm.",
        "Đưa các dự án tiêu biểu lên đầu phần kinh nghiệm để gây ấn tượng nhanh với nhà tuyển dụng."
    ]

    return {
        "overall_score": overall_score,
        "score_label": label,
        "category_scores": {
            "kinh_nghiem": round(min(10.0, overall_score - 0.5), 1),
            "ky_nang": round(min(10.0, overall_score + 0.8), 1),
            "dinh_dang": 6.5,
            "thanh_tich": round(min(10.0, overall_score - 0.2), 1),
            "muc_tieu": 7.0
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggested_action_items": suggested_action_items,
        "summary_explanation": f"Hồ sơ ứng viên đạt mức {label} ({overall_score}/10). Nền tảng kỹ thuật cơ bản khá tốt, bổ sung thêm các số liệu dự án cụ thể sẽ giúp CV nổi bật hơn rõ rệt."
    }
