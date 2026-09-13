# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.recruiter_enums import (
    CriteriaSetStatus,
    CriterionCategory,
    CriterionImportance,
    CriterionOperator,
)


class ScreeningCriteriaSet(Base):
    __tablename__ = "screening_criteria_sets"
    __table_args__ = (
        UniqueConstraint("job_id", "version_number", name="uq_job_criteria_version"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CriteriaSetStatus.DRAFT.value, index=True
    )
    scoring_weights: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    published_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    criteria = relationship(
        "Criterion",
        back_populates="criteria_set",
        cascade="all, delete-orphan",
        order_by="Criterion.sort_order",
        lazy="selectin",
    )


class Criterion(Base):
    __tablename__ = "screening_criteria"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    criteria_set_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("screening_criteria_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    importance: Mapped[str] = mapped_column(String(30), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    operator: Mapped[str] = mapped_column(String(30), nullable=False)
    expected_value: Mapped[object] = mapped_column(JSON, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    criteria_set = relationship("ScreeningCriteriaSet", back_populates="criteria")

    @staticmethod
    def enum_values() -> dict[str, list[str]]:
        return {
            "category": [item.value for item in CriterionCategory],
            "importance": [item.value for item in CriterionImportance],
            "operator": [item.value for item in CriterionOperator],
        }
