# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

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

class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_years_experience: Optional[int] = None
    required_education: Optional[str] = None
    weight_skills: Optional[float] = None
    weight_experience: Optional[float] = None
    weight_education: Optional[float] = None

class JobPostingResponse(JobPostingBase):
    id: str
    status: str
    active_criteria_set_id: Optional[str] = None
    version: int = 1
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
