# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, JSON, Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class RealJobPosting(Base):
    __tablename__ = "real_job_postings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="TopCV") # TopCV, ITViec, Manual Feed
    external_id: Mapped[str] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_logo_url: Mapped[str] = mapped_column(String(512), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    location_tag: Mapped[str] = mapped_column(String(50), default="OTHER") # HA_NOI, HO_CHI_MINH, DA_NANG, REMOTE, OTHER
    salary_text: Mapped[str] = mapped_column(String(255), nullable=True)
    salary_min_vnd: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    salary_max_vnd: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    required_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    experience_required: Mapped[str] = mapped_column(String(255), nullable=True)
    description_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    matches = relationship("CandidateJobMatch", back_populates="real_job", cascade="all, delete-orphan")

class CandidateJobMatch(Base):
    __tablename__ = "candidate_job_matches"
    __table_args__ = (UniqueConstraint("resume_id", "real_job_id", name="uq_resume_realjob"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False)
    real_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("real_job_postings.id", ondelete="CASCADE"), nullable=False)
    
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    skills_sub_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    experience_sub_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    strengths_summary: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    gaps_summary: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    match_reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    saved_status: Mapped[str] = mapped_column(String(50), default="DEFAULT") # DEFAULT, SAVED, APPLIED
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    real_job = relationship("RealJobPosting", back_populates="matches")
