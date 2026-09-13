# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RecruitmentDecisionEvent(Base):
    __tablename__ = "recruitment_decision_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    from_stage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    to_stage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reason_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    before_version: Mapped[int] = mapped_column(Integer, nullable=False)
    after_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
