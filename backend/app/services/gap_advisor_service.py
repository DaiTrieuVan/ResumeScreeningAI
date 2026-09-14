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
You are an expert Career Advisor and Technical Mentor.
Evaluate the candidate's CV against the target Job Description to produce an actionable career gap analysis.

### Target Job Title: {job_title}
### Target Job Description:
{job_description}

### Candidate CV Content:
{cv_text}

### Instructions:
Return a strict JSON object with this schema:
{{
  "matched_skills": ["Skill 1", "Skill 2"],
  "missing_skills": ["Missing Skill 1", "Missing Requirement 2"],
  "suggested_action_items": [
    "Concrete suggestion 1 (e.g. Learn FastAPI & async ORMs)",
    "Concrete suggestion 2 (e.g. Build a portfolio project demonstrating Docker deployment)"
  ],
  "summary_explanation": "Encouraging, clear summary of candidate fit and major areas to address."
}}
"""

async def analyze_career_gap(
    job_title: str,
    job_description: str,
    cv_text: str
) -> Dict[str, Any]:
    prompt = GAP_PROMPT_TEMPLATE.format(
        job_title=job_title or "Target Role",
        job_description=job_description[:3000],
        cv_text=cv_text[:3000]
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
    return {
        "matched_skills": list(data.get("matched_skills") or []),
        "missing_skills": list(data.get("missing_skills") or []),
        "suggested_action_items": list(data.get("suggested_action_items") or []),
        "summary_explanation": str(data.get("summary_explanation") or "Career gap analysis complete.")
    }

def fallback_gap_analysis(job_description: str, cv_text: str) -> Dict[str, Any]:
    jd_words = set(job_description.lower().split())
    cv_words = set(cv_text.lower().split())
    
    # Common tech keywords check
    common_keywords = ["python", "react", "fastapi", "docker", "sql", "postgresql", "rest", "api", "git", "aws", "kubernetes", "typescript"]
    matched = [k for k in common_keywords if k in jd_words and k in cv_words]
    missing = [k for k in common_keywords if k in jd_words and k not in cv_words]

    return {
        "matched_skills": matched or ["CV uploaded text"],
        "missing_skills": missing or ["Advanced System Architecture"],
        "suggested_action_items": [
            f"Build hands-on experience in missing technologies: {', '.join(missing[:3]) if missing else 'cloud deployments'}",
            "Highlight measurable impact and key project metrics in CV work history entries."
        ],
        "summary_explanation": "Solid foundation identified. Focus on acquiring experience in key target job keywords to maximize candidacy."
    }
