from typing import Optional, List
from pydantic import BaseModel, Field

class RecruiterStatusUpdate(BaseModel):
    recruiter_status: str = Field(..., example="SHORTLISTED") # NEW, SHORTLISTED, UNDER_REVIEW, REJECTED
    recruiter_feedback_notes: Optional[str] = None
    score_override: Optional[float] = None
