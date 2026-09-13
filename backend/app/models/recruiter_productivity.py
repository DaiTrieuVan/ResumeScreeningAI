# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SavedView(Base):
    __tablename__ = "recruiter_saved_views"
    __table_args__ = (UniqueConstraint("owner_id", "job_id", "name", name="uq_saved_view_owner_job_name"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    columns: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    filters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    sort: Mapped[str] = mapped_column(String(30), nullable=False, default="score_desc")
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CandidateTag(Base):
    __tablename__ = "candidate_tags"
    __table_args__ = (UniqueConstraint("normalized_name", name="uq_candidate_tag_name"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(80), nullable=False)


class CandidateTagAssignment(Base):
    __tablename__ = "candidate_tag_assignments"
    __table_args__ = (UniqueConstraint("application_id", "tag_id", name="uq_application_tag"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_tags.id", ondelete="CASCADE"), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tag = relationship("CandidateTag", lazy="joined")


class BulkActionRequest(Base):
    __tablename__ = "bulk_action_requests"
    __table_args__ = (UniqueConstraint("actor_id", "idempotency_key", name="uq_bulk_actor_key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    items = relationship("BulkActionItem", cascade="all, delete-orphan", lazy="selectin")


class BulkActionItem(Base):
    __tablename__ = "bulk_action_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("bulk_action_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id: Mapped[str] = mapped_column(String(36), nullable=False)
    expected_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    resulting_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
