# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class GapAnalysisRequest(BaseModel):
    job_title: Optional[str] = Field(None, example="Senior Fullstack Engineer")
    job_description: str = Field(..., example="Seeking 4+ years of Python and React experience...")
    cv_text: Optional[str] = None

class GapAnalysisResponse(BaseModel):
    id: str
    target_job_title: Optional[str] = None
    overall_score: float = Field(7.5, description="Overall CV score out of 10")
    score_label: str = Field("Tốt", description="Rating label (Xuất sắc, Tốt, Khá, Cần cải thiện)")
    category_scores: Dict[str, float] = Field(default_factory=dict, description="Category scores out of 10")
    category_details: Dict[str, str] = Field(default_factory=dict, description="Detailed qualitative feedback for each category")
    strengths: List[str] = Field(default_factory=list, description="List of CV strengths")
    weaknesses: List[str] = Field(default_factory=list, description="List of CV weaknesses")
    spelling_and_format_errors: List[str] = Field(default_factory=list, description="Detected spelling or formatting issues in CV")
    matched_skills: List[str]
    missing_skills: List[str]
    suggested_action_items: List[str]
    summary_explanation: str
    created_at: datetime
