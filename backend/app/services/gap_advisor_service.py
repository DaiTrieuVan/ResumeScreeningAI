# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import json
import logging
import re
from typing import Dict, Any
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)


_SKILL_ALIASES = (
    ("Spring Boot", ("spring boot", "springboot")),
    ("RESTful API", ("restful api", "rest api")),
    ("PostgreSQL", ("postgresql", "postgres")),
    ("JavaScript", ("javascript",)),
    ("TypeScript", ("typescript",)),
    ("FastAPI", ("fastapi",)),
    ("MySQL", ("mysql",)),
    ("Kubernetes", ("kubernetes",)),
    ("Docker", ("docker",)),
    ("Python", ("python",)),
    ("Java", ("java",)),
    ("React", ("react",)),
    ("Redis", ("redis",)),
    ("Kafka", ("kafka",)),
    ("AWS", ("aws",)),
    ("SQL", ("sql",)),
    ("Git", ("git",)),
)


def _canonical_skill_name(value: Any) -> str:
    """Return a stable display name without changing unknown technologies."""
    cleaned = re.sub(r"\s+", " ", str(value or "")).strip(" ,;\t\r\n")
    folded = cleaned.casefold()
    for canonical, aliases in _SKILL_ALIASES:
        if folded in aliases:
            return canonical
    return cleaned


def _normalize_skill_list(values: Any) -> list[str]:
    """Canonicalize, join known multi-word skills, and remove duplicates."""
    if not isinstance(values, (list, tuple, set)):
        values = [values] if values else []

    cleaned = [_canonical_skill_name(value) for value in values]
    cleaned = [value for value in cleaned if value]

    merged: list[str] = []
    index = 0
    while index < len(cleaned):
        pair = " ".join(cleaned[index:index + 2]).casefold()
        if pair == "spring boot":
            merged.append("Spring Boot")
            index += 2
        elif pair in {"rest api", "restful api"}:
            merged.append("RESTful API")
            index += 2
        else:
            merged.append(_canonical_skill_name(cleaned[index]))
            index += 1

    unique: list[str] = []
    seen: set[str] = set()
    for skill in merged:
        key = skill.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(skill)
    return unique


def _normalize_technical_text(value: Any) -> str:
    """Repair common LLM/fallback splits inside human-readable feedback."""
    text = str(value or "")
    replacements = (
        (r"\bSpring\s*,\s*Boot\b", "Spring Boot"),
        (r"\bREST(?:ful)?\s*,\s*API\b", "RESTful API"),
        (r"\bPostgresql\b", "PostgreSQL"),
        (r"\bMysql\b", "MySQL"),
        (r"\bJavascript\b", "JavaScript"),
        (r"\bTypescript\b", "TypeScript"),
        (r"\bFastapi\b", "FastAPI"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

GAP_PROMPT_TEMPLATE = """
You are a Vice President of Engineering and Principal Technical Recruiter conducting an in-depth CV evaluation against a target Job Description.
Evaluate the candidate's CV strictly, constructively, and professionally based on realistic engineering recruitment standards.

### CRITICAL EVALUATION RULES:
1. **Spell & Tech Term Standardizer ("spelling_and_format_errors"):**
   - Detect spelling mistakes in Vietnamese or English (e.g. "hệ thông" ➔ "hệ thống", "Developement" ➔ "Development").
   - Detect incorrect tech term capitalization/formatting (e.g. "springboot" ➔ "Spring Boot", "postgres" ➔ "PostgreSQL", "pyton" ➔ "Python", "javascript" ➔ "JavaScript").
   - List each detected error as a string: "Lỗi chính tả/từ khóa: 'springboot' ➔ Nên sửa thành 'Spring Boot'".

2. **Targeted Value Proposition ("Sell what they need, not everything you have"):**
   - Flag irrelevant "noise" skills that dilute the candidate's focus (e.g., listing Java/PHP when applying for an AI/ML position).
   - Guide the candidate to emphasize exact requirements from the Job Description.

3. **Skill Organization & Proficiency Level:**
   - Check whether Skills are positioned prominently and described using clear contextual proficiency levels (e.g. "Proficient", "Working Knowledge") rather than meaningless percentage bars.

4. **Project Impact & Lessons Learned:**
   - Penalize generic feature lists (e.g. "Built login & shopping cart").
   - Require individual contribution details and technical lessons learned / challenges solved (e.g. "Handled concurrency race conditions", "Optimized DB query latency by 40%").

### Target Job Title: {job_title}
### Target Job Description:
{job_description}

### Candidate CV Content:
{cv_text}

### Instructions:
Treat multi-word technology names as one indivisible skill. In particular, return
"Spring Boot" and "RESTful API" as single array items; never split them into
"Spring"/"Boot" or "REST"/"API".
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
  "category_details": {{
    "kinh_nghiem": "Kinh nghiệm thực hành tốt nhưng cần mô tả rõ hơn quy mô dữ liệu và bài học giải quyết lỗi thực tế.",
    "ky_nang": "Nắm chắc các công nghệ trọng tâm; cần bổ sung các công nghệ nâng cao được yêu cầu trong JD.",
    "dinh_dang": "Bố cục rõ ràng, dễ nhìn; cần rà soát khoảng trắng dấu câu và chuẩn hóa viết hoa đúng tên công nghệ.",
    "thanh_tich": "Có số liệu bước đầu về hiệu năng, nên lượng hóa cụ thể hơn với các chỉ số đo lường như % tối ưu, latency.",
    "muc_tieu": "Mục tiêu rõ định hướng nghề nghiệp, nên gắn kết chặt chẽ hơn với định hướng của vị trí ứng tuyển."
  }},
  "strengths": [
    "Nền tảng kỹ thuật tốt về Java backend, đặc biệt là Spring Boot, cơ sở dữ liệu và RESTful API.",
    "Kết quả học tập rất tốt với GPA ấn tượng, thể hiện khả năng tiếp thu và tư duy logic mạnh mẽ.",
    "Kinh nghiệm làm dự án có số liệu cụ thể về quy mô và hiệu năng hệ thống."
  ],
  "weaknesses": [
    "Mô tả dự án còn thiên về liệt kê tính năng chung chung, chưa làm nổi bật vai trò cá nhân và thách thức kỹ thuật đã giải quyết.",
    "Một số kỹ năng chưa tập trung vào yêu cầu cốt lõi của JD, gây nhiễu thông tin khi duyệt nhanh.",
    "Khoảng cách dấu câu và định dạng một số dòng chưa tối ưu cho công cụ quét CV (ATS)."
  ],
  "spelling_and_format_errors": [
    "Lỗi từ khóa: 'springboot' ➔ Nên ghi chuẩn là 'Spring Boot'",
    "Lỗi từ khóa: 'postgres' ➔ Nên ghi chuẩn là 'PostgreSQL'"
  ],
  "matched_skills": ["Java", "Spring Boot", "RESTful API", "MySQL"],
  "missing_skills": ["Docker", "Redis", "PostgreSQL", "Kafka"],
  "suggested_action_items": [
    "Tái cấu trúc mô tả dự án: Nêu rõ vai trò cá nhân, thách thức kỹ thuật và bài học rút ra thay vì chỉ liệt kê tính năng.",
    "Tập trung phần kỹ năng vào các công nghệ trọng tâm của JD, ẩn bớt thông tin không liên quan.",
    "Chuẩn hóa lại các từ khóa công nghệ (Spring Boot, PostgreSQL) và căn chỉnh khoảng trắng dấu câu."
  ],
  "summary_explanation": "Hồ sơ có tư duy kỹ thuật khá vững. Tối ưu lại mô tả dự án theo bài học kinh nghiệm và chuẩn hóa từ khóa sẽ giúp CV có sức thuyết phục cao hơn hẳn."
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
            response = None
            candidate_models = [settings.DEFAULT_LLM_MODEL, "gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.8-flash", "gemini-flash-latest"]
            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.3
                        )
                    )
                    if response and response.text:
                        break
                except Exception as me:
                    err_msg = str(me).lower()
                    if "404" in err_msg or "not found" in err_msg or "no longer available" in err_msg:
                        logger.warning(f"Model {model_name} unavailable, trying next candidate model...")
                        continue
                    raise me

            if not response or not response.text:
                logger.warning("No valid response from Gemini models, falling back to rule-based gap analysis...")
                return fallback_gap_analysis(job_description, cv_text)

            raw_text = response.text.strip()
            data = json.loads(raw_text)
            return sanitize_gap_output(data, job_description, cv_text)
        except Exception as e:
            logger.error(f"Gemini API error during gap analysis: {e}")
            return fallback_gap_analysis(job_description, cv_text)
    else:
        return fallback_gap_analysis(job_description, cv_text)

def sanitize_gap_output(data: Dict[str, Any], job_description: str = "", cv_text: str = "") -> Dict[str, Any]:
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

    cat_det = data.get("category_details") or {}
    category_details = {
        "kinh_nghiem": _normalize_technical_text(cat_det.get("kinh_nghiem") or "Kinh nghiệm thực hành tốt nhưng cần mô tả rõ hơn quy mô dữ liệu và bài học giải quyết lỗi thực tế."),
        "ky_nang": _normalize_technical_text(cat_det.get("ky_nang") or "Nắm chắc các công nghệ trọng tâm; cần bổ sung các công nghệ nâng cao được yêu cầu trong JD."),
        "dinh_dang": _normalize_technical_text(cat_det.get("dinh_dang") or "Bố cục rõ ràng, dễ nhìn; cần rà soát khoảng trắng dấu câu và chuẩn hóa viết hoa đúng tên công nghệ."),
        "thanh_tich": _normalize_technical_text(cat_det.get("thanh_tich") or "Có số liệu bước đầu về hiệu năng, nên lượng hóa cụ thể hơn với các chỉ số đo lường như % tối ưu, latency."),
        "muc_tieu": _normalize_technical_text(cat_det.get("muc_tieu") or "Mục tiêu rõ định hướng nghề nghiệp, nên gắn kết chặt chẽ hơn với định hướng của vị trí ứng tuyển.")
    }

    strengths = list(data.get("strengths") or [])
    weaknesses = list(data.get("weaknesses") or [])
    matched_skills = _normalize_skill_list(data.get("matched_skills") or [])
    missing_skills = _normalize_skill_list(data.get("missing_skills") or [])
    suggested_action_items = list(data.get("suggested_action_items") or [])

    # Guarantee fallback if LLM returned empty arrays
    if not strengths or not weaknesses or not suggested_action_items:
        fb = fallback_gap_analysis(job_description or "Developer", cv_text or "Candidate Resume")
        if not strengths:
            strengths = fb["strengths"]
        if not weaknesses:
            weaknesses = fb["weaknesses"]
        if not suggested_action_items:
            suggested_action_items = fb["suggested_action_items"]
        if not matched_skills:
            matched_skills = fb["matched_skills"]
        if not missing_skills:
            missing_skills = fb["missing_skills"]

    return {
        "overall_score": overall_score,
        "score_label": label,
        "category_scores": category_scores,
        "category_details": category_details,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "spelling_and_format_errors": list(data.get("spelling_and_format_errors") or []),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggested_action_items": suggested_action_items,
        "summary_explanation": str(data.get("summary_explanation") or f"Hồ sơ đạt mức {label} ({overall_score}/10). Tối ưu lại phần mô tả dự án theo bài học thực tế và bổ sung từ khóa kỹ thuật sẽ giúp CV ấn tượng hơn hẳn.")
    }

def fallback_gap_analysis(job_description: str, cv_text: str) -> Dict[str, Any]:
    def contains_alias(text: str, aliases: tuple[str, ...]) -> bool:
        normalized = re.sub(r"[^a-z0-9+#.]+", " ", text.casefold()).strip()
        padded = f" {normalized} "
        return any(f" {alias} " in padded for alias in aliases)

    matched = []
    missing = []
    for canonical, aliases in _SKILL_ALIASES:
        if contains_alias(job_description, aliases):
            target = matched if contains_alias(cv_text, aliases) else missing
            target.append(canonical)

    if not matched:
        matched = ["REST API", "Java Core", "Git"]
    if not missing:
        missing = ["PostgreSQL", "Docker", "CI/CD"]

    # Simple offline spelling/tech term check simulation
    detected_typos = []
    text_lower = cv_text.lower()
    if "springboot" in text_lower:
        detected_typos.append("Lỗi từ khóa: 'springboot' ➔ Nên ghi chuẩn là 'Spring Boot'")
    if "postgres" in text_lower and "postgresql" not in text_lower:
        detected_typos.append("Lỗi từ khóa: 'postgres' ➔ Nên ghi chuẩn là 'PostgreSQL'")
    if "pyton" in text_lower:
        detected_typos.append("Lỗi chính tả: 'pyton' ➔ Nên sửa thành 'Python'")
    if not detected_typos:
        detected_typos = ["Lỗi trình bày: Cần kiểm tra lại khoảng trắng trước dấu câu (ví dụ: 'API , MySQL .')"]

    match_ratio = len(matched) / (len(matched) + len(missing)) if (matched or missing) else 0.6
    overall_score = round(min(9.5, max(5.0, 5.5 + match_ratio * 4.0)), 1)
    
    if overall_score >= 8.5: label = "Xuất sắc"
    elif overall_score >= 7.0: label = "Tốt"
    elif overall_score >= 5.5: label = "Khá"
    else: label = "Cần cải thiện"

    strengths = [
        f"Nền tảng kỹ thuật phù hợp với các kỹ năng cốt lõi: {', '.join(matched[:4])}.",
        "Cấu trúc phân chia các mục cơ bản rõ ràng, dễ theo dõi.",
        "Có tinh thần chủ động thực hiện dự án thực tế."
    ]

    weaknesses = [
        f"CV còn thiếu các từ khóa kỹ thuật yêu cầu trong JD: {', '.join(missing[:3])}.",
        "Mô tả dự án còn thiên về liệt kê tính năng, chưa nêu bật vai trò cá nhân và bài học/thách thức kỹ thuật.",
        "Phần kỹ năng chưa phân loại rõ ràng theo độ thành thạo chuyên môn."
    ]

    suggested_action_items = [
        f"Tập trung bổ sung các từ khóa kỹ thuật yêu cầu còn thiếu: {', '.join(missing[:3])}.",
        "Viết lại phần dự án: Mô tả rõ vai trò cá nhân, bài học kinh nghiệm và kết quả đo lường được.",
        "Chuẩn hóa lại chính tả từ khóa công nghệ và tăng khoảng thoáng định dạng cho ATS."
    ]

    category_details = {
        "kinh_nghiem": f"Kinh nghiệm thực hành tốt nhưng cần tăng cường thêm bối cảnh nhóm và bài học kỹ thuật khi đối mặt với lỗi/bug lớn.",
        "ky_nang": f"Đã thể hiện tốt các kỹ năng: {', '.join(matched[:3])}. Cần bổ sung thêm: {', '.join(missing[:3])} để đáp ứng trọn vẹn JD.",
        "dinh_dang": "Bố cục phân mục cơ bản tốt; chú ý căn lề, khoảng cách dòng và rà soát lỗi viết dính từ hoặc khoảng trắng trước dấu phẩy.",
        "thanh_tich": "Dự án đã có thông tin triển khai; nên lượng hóa thêm các chỉ số kết quả (như thời gian phản hồi, số người dùng, % tối ưu).",
        "muc_tieu": "Mục tiêu đã định hình rõ vị trí; nên diễn đạt hướng tới giải quyết bài toán kinh doanh/sản phẩm của doanh nghiệp."
    }

    return {
        "overall_score": overall_score,
        "score_label": label,
        "category_scores": {
            "kinh_nghiem": round(min(10.0, overall_score - 0.5), 1),
            "ky_nang": round(min(10.0, overall_score + 0.8), 1),
            "dinh_dang": 6.0,
            "thanh_tich": round(min(10.0, overall_score - 0.2), 1),
            "muc_tieu": 7.0
        },
        "category_details": category_details,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "spelling_and_format_errors": detected_typos,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggested_action_items": suggested_action_items,
        "summary_explanation": f"Hồ sơ đạt mức {label} ({overall_score}/10). Tối ưu lại phần mô tả dự án theo bài học thực tế và chuẩn hóa chính tả sẽ giúp CV ấn tượng hơn hẳn."
    }
