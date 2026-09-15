# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceResponse(BaseModel):
    id: str
    page_number: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    excerpt: str
    polarity: str
    confidence: float
    source_method: str = "LEGACY_UNKNOWN"
    model_config = ConfigDict(from_attributes=True)


class CriterionResultResponse(BaseModel):
    id: str
    criterion_id: str
    label: str
    importance: str
    result: str
    score: float | None = None
    confidence: float
    explanation: str
    needs_manual_review: bool
    evidence: list[EvidenceResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class EvaluationResponse(BaseModel):
    id: str
    criteria_set_id: str | None = None
    evaluation_kind: str
    component_scores: dict[str, float]
    overall_score: float
    maximum_possible_score: float = 100.0
    evidence_coverage: float = 0.0
    scoring_version: str = "legacy"
    mandatory_gate: str
    evidence_status: str
    evaluated_at: datetime
    criterion_results: list[CriterionResultResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class CandidateDetailResponse(BaseModel):
    application_id: str
    application_version: int
    evaluation_stale: bool = False
    stale_reason: str | None = None
    privacy_mode: str = "IDENTIFIED"
    resume_available: bool = True
    job_id: str
    resume_id: str
    pipeline_stage: str
    candidate_name: str
    candidate_email: str | None = None
    candidate_phone: str | None = None
    file_name: str
    extracted_skills: list[str] = Field(default_factory=list)
    work_history: list = Field(default_factory=list)
    education: list = Field(default_factory=list)
    field_confidence: dict[str, float | None] = Field(default_factory=dict)
    evaluation: EvaluationResponse | None = None
