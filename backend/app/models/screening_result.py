# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, JSON, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ScreeningResult(Base):
    __tablename__ = "screening_results"
    __table_args__ = (UniqueConstraint("job_id", "resume_id", name="uq_job_resume"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False)
    
    stage1_similarity_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    skills_sub_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    experience_sub_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    education_sub_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    
    skills_summary: Mapped[str] = mapped_column(Text, nullable=True)
    experience_summary: Mapped[str] = mapped_column(Text, nullable=True)
    education_summary: Mapped[str] = mapped_column(Text, nullable=True)

    strengths_summary: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    gaps_summary: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    
    recruiter_status: Mapped[str] = mapped_column(String(50), default="NEW") # NEW, SHORTLISTED, UNDER_REVIEW, REJECTED
    recruiter_feedback_notes: Mapped[str] = mapped_column(Text, nullable=True)
    score_override: Mapped[float] = mapped_column(Float, nullable=True)
    criteria_set_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    evaluation_kind: Mapped[str] = mapped_column(String(20), nullable=False, default="LEGACY")
    
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job = relationship("JobPosting", back_populates="screenings")
    resume = relationship("CandidateResume", back_populates="screenings")
