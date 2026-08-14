from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class GapAnalysisRequest(BaseModel):
    job_title: Optional[str] = Field(None, example="Senior Fullstack Engineer")
    job_description: str = Field(..., example="Seeking 4+ years of Python and React experience...")
    cv_text: Optional[str] = None

class GapAnalysisResponse(BaseModel):
    id: str
    target_job_title: Optional[str] = None
    matched_skills: List[str]
    missing_skills: List[str]
    suggested_action_items: List[str]
    summary_explanation: str
    created_at: datetime
