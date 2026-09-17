# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class GapAnalysis(Base):
    __tablename__ = "gap_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    target_job_title: Mapped[str] = mapped_column(String(255), nullable=True)
    target_job_description: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=True, default=7.5)
    score_label: Mapped[str] = mapped_column(String(50), nullable=True, default="Tốt")
    category_scores: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    strengths: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    weaknesses: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    matched_skills: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    suggested_action_items: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    summary_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
