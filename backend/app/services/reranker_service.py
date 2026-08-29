import json
import logging
from typing import Dict, Any, List
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

RERANK_PROMPT_TEMPLATE = """
You are an expert AI Talent Acquisition and Technical Recruiter evaluating candidate resumes against job requisitions.
Evaluate the candidate resume below against the job requirements.

### Job Description / Requirements:
Title: {job_title}
Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Min Years Experience: {min_experience}
Required Education: {required_education}

### Candidate Resume Content:
{resume_text}

### Instructions:
1. Carefully assess the overlap between candidate skills/experience and the job requirements.
2. Return a strict JSON object matching this schema:
{{
  "candidate_name": "Extracted candidate name",
  "email": "Extracted email",
  "phone": "Extracted phone",
  "skills_sub_score": <float 0 to 100>,
  "experience_sub_score": <float 0 to 100>,
  "education_sub_score": <float 0 to 100>,
  "skills_summary": "Short 1-line summary of candidate's key technical skills",
  "experience_summary": "Short 1-line summary of candidate's work experience and years",
  "education_summary": "Short 1-line summary of candidate's degree and university",
  "strengths_summary": ["Strength point 1", "Strength point 2"],
  "gaps_summary": ["Missing requirement 1", "Missing requirement 2"],
  "ai_reasoning": "Detailed plain-language explanation summarizing the candidate's alignment with the role."
}}
"""

async def rerank_candidate_resume(
    job_title: str,
    required_skills: List[str],
    preferred_skills: List[str],
    min_experience: int,
    required_education: str,
    resume_text: str
) -> Dict[str, Any]:
    """
    Calls Gemini 1.5 Flash to generate structured evaluations.
    """
    prompt = RERANK_PROMPT_TEMPLATE.format(
        job_title=job_title,
        required_skills=", ".join(required_skills or []),
        preferred_skills=", ".join(preferred_skills or []),
        min_experience=min_experience,
        required_education=required_education or "Not specified",
        resume_text=resume_text[:4000] # Cap text length to prevent overflow
    )

    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.DEFAULT_LLM_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)
            return sanitize_rerank_output(parsed, required_skills, resume_text)
        except Exception as e:
            logger.error(f"Gemini API error during rerank: {e}")
            return heuristic_fallback_eval(job_title, required_skills, min_experience, resume_text)
    else:
        # Fallback heuristic evaluation when GEMINI_API_KEY is not set
        return heuristic_fallback_eval(job_title, required_skills, min_experience, resume_text)

def sanitize_rerank_output(data: Dict[str, Any], required_skills: List[str] = None, resume_text: str = "") -> Dict[str, Any]:
    skills_sum = str(data.get("skills_summary") or "").strip()
    if not skills_sum and required_skills and resume_text:
        text_lower = resume_text.lower()
        matched = [s for s in required_skills if s.lower() in text_lower]
        skills_sum = ", ".join(matched) if matched else "Kỹ năng cơ bản"

    exp_sum = str(data.get("experience_summary") or "").strip()
    if not exp_sum:
        exp_sum = "Có kinh nghiệm thực tế trong ngành"

    edu_sum = str(data.get("education_summary") or "").strip()
    if not edu_sum:
        edu_sum = "Đại học / Cao đẳng chuyên ngành phù hợp"

    return {
        "candidate_name": str(data.get("candidate_name") or "Unknown Candidate"),
        "email": str(data.get("email") or ""),
        "phone": str(data.get("phone") or ""),
        "skills_sub_score": float(max(0.0, min(100.0, data.get("skills_sub_score", 50.0)))),
        "experience_sub_score": float(max(0.0, min(100.0, data.get("experience_sub_score", 50.0)))),
        "education_sub_score": float(max(0.0, min(100.0, data.get("education_sub_score", 50.0)))),
        "skills_summary": skills_sum,
        "experience_summary": exp_sum,
        "education_summary": edu_sum,
        "strengths_summary": list(data.get("strengths_summary") or []),
        "gaps_summary": list(data.get("gaps_summary") or []),
        "ai_reasoning": str(data.get("ai_reasoning") or "Evaluation complete.")
    }

def heuristic_fallback_eval(
    job_title: str,
    required_skills: List[str],
    min_experience: int,
    resume_text: str
) -> Dict[str, Any]:
    """
    Deterministic rule-based fallback when offline or API key missing.
    """
    text_lower = resume_text.lower()
    matched_skills = [s for s in required_skills if s.lower() in text_lower]
    missing_skills = [s for s in required_skills if s.lower() not in text_lower]
    
    skills_score = (len(matched_skills) / len(required_skills) * 100.0) if required_skills else 70.0
    exp_score = 80.0 if "year" in text_lower or "experience" in text_lower else 50.0
    edu_score = 85.0 if any(deg in text_lower for deg in ["bachelor", "master", "degree", "university", "bs", "ms"]) else 60.0

    skills_summary_text = f"Đã khớp: {', '.join(matched_skills)}" if matched_skills else "Có kỹ năng liên quan"
    exp_summary_text = "Có kinh nghiệm thực tế liên quan"
    if "year" in text_lower:
        exp_summary_text = "Khoảng 2-4 năm kinh nghiệm làm việc"
    edu_summary_text = "Cử nhân / Kỹ sư Chuyên ngành CNTT"

    return {
        "candidate_name": "Candidate Profile",
        "email": "",
        "phone": "",
        "skills_sub_score": round(skills_score, 1),
        "experience_sub_score": round(exp_score, 1),
        "education_sub_score": round(edu_score, 1),
        "skills_summary": skills_summary_text,
        "experience_summary": exp_summary_text,
        "education_summary": edu_summary_text,
        "strengths_summary": [f"Matched skill: {s}" for s in matched_skills] or ["Extracted resume text"],
        "gaps_summary": [f"Missing required skill: {s}" for s in missing_skills] or ["None identified"],
        "ai_reasoning": f"Heuristic evaluation against {job_title}: Matched {len(matched_skills)} of {len(required_skills)} required skills."
    }
