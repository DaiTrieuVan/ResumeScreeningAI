# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.recruiter_enums import EvaluationKind, MandatoryGate, PipelineStage


class CandidateApplication(Base):
    __tablename__ = "candidate_applications"
    __table_args__ = (
        UniqueConstraint("job_id", "resume_id", name="uq_job_resume_application"),
        Index("ix_application_job_stage_updated", "job_id", "pipeline_stage", "updated_at"),
        Index("ix_application_job_received", "job_id", "received_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    pipeline_stage: Mapped[str] = mapped_column(String(40), nullable=False, default=PipelineStage.RECEIVED.value, index=True)
    ai_recommendation: Mapped[str | None] = mapped_column(String(30), nullable=True)
    human_decision: Mapped[str | None] = mapped_column(String(30), nullable=True)
    decision_reason_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    evaluations = relationship("ScreeningEvaluation", back_populates="application", cascade="all, delete-orphan")


class ScreeningEvaluation(Base):
    __tablename__ = "screening_evaluations"
    __table_args__ = (UniqueConstraint("application_id", "input_fingerprint", name="uq_application_evaluation_input"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    criteria_set_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("screening_criteria_sets.id", ondelete="SET NULL"), nullable=True, index=True)
    screening_result_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("screening_results.id", ondelete="SET NULL"), nullable=True)
    evaluation_kind: Mapped[str] = mapped_column(String(20), nullable=False, default=EvaluationKind.OFFICIAL.value)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")
    component_scores: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    mandatory_gate: Mapped[str] = mapped_column(String(30), nullable=False, default=MandatoryGate.NEEDS_REVIEW.value)
    model_info: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    input_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PARTIAL")
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    application = relationship("CandidateApplication", back_populates="evaluations")
    criterion_results = relationship("CriterionResult", back_populates="evaluation", cascade="all, delete-orphan", lazy="selectin")


class CriterionResult(Base):
    __tablename__ = "criterion_results"
    __table_args__ = (UniqueConstraint("evaluation_id", "criterion_id", name="uq_evaluation_criterion"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id: Mapped[str] = mapped_column(String(36), ForeignKey("screening_evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_id: Mapped[str] = mapped_column(String(36), ForeignKey("screening_criteria.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    importance: Mapped[str] = mapped_column(String(30), nullable=False)
    result: Mapped[str] = mapped_column(String(30), nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    needs_manual_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    evaluation = relationship("ScreeningEvaluation", back_populates="criterion_results")
    evidence = relationship("EvidenceSnippet", back_populates="criterion_result", cascade="all, delete-orphan", lazy="selectin")


class EvidenceSnippet(Base):
    __tablename__ = "evidence_snippets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    criterion_result_id: Mapped[str] = mapped_column(String(36), ForeignKey("criterion_results.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    polarity: Mapped[str] = mapped_column(String(20), nullable=False, default="SUPPORTS")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    criterion_result = relationship("CriterionResult", back_populates="evidence")
