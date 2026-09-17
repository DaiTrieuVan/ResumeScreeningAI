# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


CORRECTABLE_FIELDS = {
    "parsed_name", "parsed_email", "parsed_phone", "extracted_skills", "work_history", "education"
}


class CorrectionRequest(BaseModel):
    field_path: str
    new_value: Any
    reason: str = Field(min_length=3, max_length=500)
    evidence_id: str | None = None

    @field_validator("field_path")
    @classmethod
    def allow_supported_fields(cls, value: str) -> str:
        if value not in CORRECTABLE_FIELDS:
            raise ValueError("Trường dữ liệu này không được phép chỉnh sửa.")
        return value


class ManualRecoveryRequest(BaseModel):
    mode: Literal["VERIFIED_TEXT"] = "VERIFIED_TEXT"
    verified_text: str = Field(min_length=20)
    reason: str = Field(min_length=3, max_length=500)


class ReviewPrivacyPolicyUpdate(BaseModel):
    mode: Literal["IDENTIFIED", "BLIND"]
    reveal_stage: str | None = None


class EvaluationRunRequest(BaseModel):
    dataset_version: str = Field(min_length=1)
    release_version: str = Field(min_length=1)
    commit_sha: str = Field(pattern=r"^[0-9a-f]{7,40}$")
    fallback_mode: bool
    model_metadata: dict[str, Any] = Field(default_factory=dict)

