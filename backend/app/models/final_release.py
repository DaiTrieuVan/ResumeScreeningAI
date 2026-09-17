# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class ResumePage(Base):
    __tablename__ = "resume_pages"
    __table_args__ = (UniqueConstraint("resume_id", "page_number", name="uq_resume_page_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    normalized_end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(20), nullable=False, default="NATIVE")
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)


class CandidateCorrection(Base):
    __tablename__ = "candidate_corrections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    field_path: Mapped[str] = mapped_column(String(80), nullable=False)
    old_value_redacted: Mapped[dict | list | str | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | list | str | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_page_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("resume_pages.id", ondelete="SET NULL"), nullable=True)
    evidence_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("evidence_snippets.id", ondelete="SET NULL"), nullable=True)
    affects_evaluation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ProcessingLease(Base):
    __tablename__ = "processing_leases"

    upload_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("upload_items.id", ondelete="CASCADE"), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False)
    lease_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    acquired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (UniqueConstraint("actor_id", "operation", "idempotency_key", name="uq_idempotency_scope_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    operation: Mapped[str] = mapped_column(String(80), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="IN_PROGRESS")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class ReviewPrivacyPolicy(Base):
    __tablename__ = "review_privacy_policies"

    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), primary_key=True)
    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="IDENTIFIED")
    reveal_stage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    masked_fields: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    dataset_id: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    release_version: Mapped[str] = mapped_column(String(50), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    criteria_versions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    model_info: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    prompt_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fallback_mode: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="QUEUED")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    report_json_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    report_md_path: Mapped[str | None] = mapped_column(String(512), nullable=True)


class MetricResult(Base):
    __tablename__ = "metric_results"
    __table_args__ = (UniqueConstraint("evaluation_run_id", "metric_name", name="uq_run_metric"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    evaluation_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    numerator: Mapped[float | None] = mapped_column(Float, nullable=True)
    denominator: Mapped[float | None] = mapped_column(Float, nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

