from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RealJobPostingResponse(BaseModel):
    id: str
    source: str
    external_id: Optional[str] = None
    title: str
    company_name: str
    company_logo_url: Optional[str] = None
    location: str
    location_tag: str
    salary_text: Optional[str] = None
    salary_min_vnd: Optional[int] = 0
    salary_max_vnd: Optional[int] = 0
    required_skills: List[str]
    experience_required: Optional[str] = None
    description_text: str
    source_url: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateJobMatchResponse(BaseModel):
    id: str
    real_job: RealJobPostingResponse
    match_score: float
    skills_sub_score: float
    experience_sub_score: float
    strengths_summary: List[str]
    gaps_summary: List[str]
    match_reasoning: str
    saved_status: str
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)
