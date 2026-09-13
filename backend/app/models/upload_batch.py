# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.recruiter_enums import (
    DuplicateResolution,
    UploadBatchStatus,
    UploadItemStatus,
)


class UploadBatch(Base):
    __tablename__ = "upload_batches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    criteria_set_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=UploadBatchStatus.CREATED.value, index=True)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    queued_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processing_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cancelled_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    items = relationship(
        "UploadItem", back_populates="batch", cascade="all, delete-orphan",
        order_by="UploadItem.created_at", lazy="selectin",
    )


class UploadItem(Base):
    __tablename__ = "upload_items"
    __table_args__ = (UniqueConstraint("batch_id", "client_file_id", name="uq_batch_client_file"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("upload_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    client_file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, default="application/pdf")
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    content_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    contact_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=UploadItemStatus.QUEUED.value, index=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    user_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    technical_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    candidate_resume_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("candidate_resumes.id", ondelete="SET NULL"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    batch = relationship("UploadBatch", back_populates="items")
    duplicate_matches = relationship(
        "DuplicateMatch",
        foreign_keys="DuplicateMatch.upload_item_id",
        back_populates="upload_item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DuplicateMatch(Base):
    __tablename__ = "duplicate_matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("upload_items.id", ondelete="CASCADE"), nullable=False, index=True)
    matched_upload_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("upload_items.id", ondelete="CASCADE"), nullable=False)
    match_type: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    resolution: Mapped[str] = mapped_column(String(40), nullable=False, default=DuplicateResolution.NEEDS_REVIEW.value)
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    upload_item = relationship("UploadItem", foreign_keys=[upload_item_id], back_populates="duplicate_matches")
