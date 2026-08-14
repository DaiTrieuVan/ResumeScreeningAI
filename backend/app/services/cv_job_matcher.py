import json
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types
from app.core.config import settings
from app.services.embedding_service import rank_candidates_by_vector_similarity

logger = logging.getLogger(__name__)

CV_JOB_MATCH_PROMPT = """
You are an expert AI Career Matcher.
Evaluate the candidate's CV against the real job opening below.

### Candidate CV:
{cv_text}

### Real Job Opening:
Title: {job_title}
Company: {company_name}
Required Skills: {required_skills}
Experience Required: {experience_required}
Job Description: {description_text}

### Instructions:
Return a strict JSON object with this schema:
{{
  "match_score": <float 0 to 100>,
  "skills_sub_score": <float 0 to 100>,
  "experience_sub_score": <float 0 to 100>,
  "why_you_fit": ["Point 1 why candidate fits this job", "Point 2"],
  "skills_gaps": ["Missing skill 1", "Missing qualification 2"],
  "match_reasoning": "Clear, encouraging explanation of why the candidate matches this role."
}}
"""

async def match_cv_against_real_jobs(
    cv_text: str,
    real_jobs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Two-stage CV-to-Jobs evaluation.
    Stage 1: Vector cosine similarity pre-ranking over real jobs.
    Stage 2: Gemini 1.5 Flash structured evaluation.
    """
    if not real_jobs or not cv_text:
        return []

    # Stage 1: Vector Pre-Ranking
    job_tuples = [(j["id"], f"{j['title']} {j['company_name']} {', '.join(j['required_skills'])} {j['description_text']}") for j in real_jobs]
    vector_rankings = dict(rank_candidates_by_vector_similarity(cv_text, job_tuples))

    # Sort real jobs by vector similarity score and take top 10
    sorted_jobs = sorted(real_jobs, key=lambda j: vector_rankings.get(j["id"], 0.0), reverse=True)[:10]

    matched_results = []
    for job in sorted_jobs:
        sim_score = vector_rankings.get(job["id"], 50.0)

        # Stage 2: Gemini LLM Rerank
        if settings.GEMINI_API_KEY:
            try:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                prompt = CV_JOB_MATCH_PROMPT.format(
                    cv_text=cv_text[:3000],
                    job_title=job["title"],
                    company_name=job["company_name"],
                    required_skills=", ".join(job["required_skills"]),
                    experience_required=job["experience_required"] or "N/A",
                    description_text=job["description_text"][:2000]
                )
                response = client.models.generate_content(
                    model=settings.DEFAULT_LLM_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                raw_json = json.loads(response.text or "{}")
                eval_data = sanitize_job_match(raw_json, sim_score)
            except Exception as e:
                logger.error(f"Gemini API error during job matching: {e}")
                eval_data = fallback_job_match(cv_text, job, sim_score)
        else:
            eval_data = fallback_job_match(cv_text, job, sim_score)

        eval_data["real_job"] = job
        matched_results.append(eval_data)

    matched_results.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_results

def sanitize_job_match(data: Dict[str, Any], sim_score: float) -> Dict[str, Any]:
    return {
        "match_score": float(max(0.0, min(100.0, data.get("match_score", sim_score)))),
        "skills_sub_score": float(max(0.0, min(100.0, data.get("skills_sub_score", 70.0)))),
        "experience_sub_score": float(max(0.0, min(100.0, data.get("experience_sub_score", 70.0)))),
        "strengths_summary": list(data.get("why_you_fit") or []),
        "gaps_summary": list(data.get("skills_gaps") or []),
        "match_reasoning": str(data.get("match_reasoning") or "Độ khớp được tính toán dựa trên kỹ năng và kinh nghiệm.")
    }

def fallback_job_match(cv_text: str, job: Dict[str, Any], sim_score: float) -> Dict[str, Any]:
    cv_lower = cv_text.lower()
    req_skills = job.get("required_skills") or []
    matched = [s for s in req_skills if s.lower() in cv_lower]
    missing = [s for s in req_skills if s.lower() not in cv_lower]

    skills_score = (len(matched) / len(req_skills) * 100.0) if req_skills else 75.0
    overall = round((skills_score * 0.6) + (sim_score * 0.4), 1)

    return {
        "match_score": overall,
        "skills_sub_score": round(skills_score, 1),
        "experience_sub_score": 80.0 if "năm" in cv_lower or "year" in cv_lower else 60.0,
        "strengths_summary": [f"Kỹ năng khớp: {s}" for s in matched] or ["Phù hợp với yêu cầu vị trí"],
        "gaps_summary": [f"Kỹ năng cần bổ sung: {s}" for s in missing] or ["Không phát hiện khoảng trống lớn"],
        "match_reasoning": f"Đã khớp {len(matched)}/{len(req_skills)} kỹ năng bắt buộc cho vị trí {job['title']} tại {job['company_name']}."
    }
