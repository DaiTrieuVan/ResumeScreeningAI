# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.recruiter_enums import DuplicateResolution, UploadBatchStatus, UploadItemStatus


class DuplicateMatchResponse(BaseModel):
    id: str
    matched_upload_item_id: str
    match_type: str
    confidence: float
    resolution: DuplicateResolution
    model_config = ConfigDict(from_attributes=True)


class UploadItemResponse(BaseModel):
    id: str
    client_file_id: str
    original_file_name: str
    byte_size: int
    status: UploadItemStatus
    error_code: str | None = None
    user_message: str | None = None
    attempt_count: int
    candidate_resume_id: str | None = None
    version: int
    duplicate_matches: list[DuplicateMatchResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class UploadBatchResponse(BaseModel):
    id: str
    job_id: str
    criteria_set_id: str | None = None
    status: UploadBatchStatus
    total_count: int
    queued_count: int
    processing_count: int
    success_count: int
    failed_count: int
    duplicate_count: int
    cancelled_count: int
    items: list[UploadItemResponse] = Field(default_factory=list)
    created_at: datetime
    completed_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class RetryBatchInput(BaseModel):
    scope: str = "FAILED_ONLY"
    item_ids: list[str] = Field(default_factory=list)


class DuplicateResolutionInput(BaseModel):
    resolution: DuplicateResolution
