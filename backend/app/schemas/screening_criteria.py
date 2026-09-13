# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.recruiter_enums import (
    CriteriaSetStatus,
    CriterionCategory,
    CriterionImportance,
    CriterionOperator,
)


class CriterionInput(BaseModel):
    category: CriterionCategory
    importance: CriterionImportance
    label: str = Field(min_length=1, max_length=255)
    operator: CriterionOperator
    expected_value: Any
    weight: float = Field(default=0.0, ge=0.0, le=1.0)
    sort_order: int = Field(default=0, ge=0)


class CriterionResponse(CriterionInput):
    id: str
    model_config = ConfigDict(from_attributes=True)


class CriteriaSetInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    scoring_weights: dict[str, float]
    criteria: list[CriterionInput] = Field(default_factory=list)

    @field_validator("scoring_weights")
    @classmethod
    def validate_weight_ranges(cls, weights: dict[str, float]) -> dict[str, float]:
        if not weights:
            raise ValueError("Cần ít nhất một nhóm trọng số.")
        if any(value < 0 or value > 1 for value in weights.values()):
            raise ValueError("Mỗi trọng số phải nằm trong khoảng 0–100%.")
        return weights


class CriteriaSetResponse(BaseModel):
    id: str
    job_id: str
    version_number: int
    name: str
    status: CriteriaSetStatus
    scoring_weights: dict[str, float]
    criteria: list[CriterionResponse]
    created_by: str
    published_by: str | None = None
    created_at: datetime
    published_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ScoreSimulationInput(BaseModel):
    component_scores: dict[str, float]
    proposed_weights: dict[str, float]


class ScoreSimulationResponse(BaseModel):
    score: float
    kind: str = "SIMULATION"
    replaces_official_score: bool = False
