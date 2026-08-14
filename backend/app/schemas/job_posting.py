from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class JobPostingBase(BaseModel):
    title: str = Field(..., example="Senior Python Developer")
    department: Optional[str] = Field(None, example="Engineering")
    required_skills: List[str] = Field(..., example=["Python", "FastAPI", "PostgreSQL"])
    preferred_skills: Optional[List[str]] = Field(default_factory=list, example=["Docker", "Redis"])
    min_years_experience: int = Field(0, ge=0, example=3)
    required_education: Optional[str] = Field(None, example="Bachelor's in Computer Science")
    weight_skills: float = Field(0.50, ge=0.0, le=1.0)
    weight_experience: float = Field(0.35, ge=0.0, le=1.0)
    weight_education: float = Field(0.15, ge=0.0, le=1.0)

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingResponse(JobPostingBase):
    id: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
