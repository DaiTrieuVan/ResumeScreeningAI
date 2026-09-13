# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from enum import Enum


class StrEnum(str, Enum):
    """JSON/database-friendly enum with stable string values."""


class CriteriaSetStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    RETIRED = "RETIRED"


class CriterionCategory(StrEnum):
    SKILL = "SKILL"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    LANGUAGE = "LANGUAGE"
    LOCATION = "LOCATION"
    OTHER = "OTHER"


class CriterionImportance(StrEnum):
    MANDATORY = "MANDATORY"
    PREFERRED = "PREFERRED"
    BONUS = "BONUS"


class CriterionOperator(StrEnum):
    CONTAINS_ANY = "CONTAINS_ANY"
    CONTAINS_ALL = "CONTAINS_ALL"
    MIN_VALUE = "MIN_VALUE"
    EQUALS = "EQUALS"
    CUSTOM_AI = "CUSTOM_AI"


class CriterionOutcome(StrEnum):
    MET = "MET"
    NOT_MET = "NOT_MET"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EvaluationKind(StrEnum):
    OFFICIAL = "OFFICIAL"
    LEGACY = "LEGACY"


class MandatoryGate(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class PipelineStage(StrEnum):
    RECEIVED = "RECEIVED"
    AI_ANALYZED = "AI_ANALYZED"
    RECRUITER_REVIEW = "RECRUITER_REVIEW"
    SHORTLISTED = "SHORTLISTED"
    HR_INTERVIEW = "HR_INTERVIEW"
    TECH_INTERVIEW = "TECH_INTERVIEW"
    OFFER = "OFFER"
    HIRED = "HIRED"
    REJECTED = "REJECTED"


class UploadBatchStatus(StrEnum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    CANCELLED = "CANCELLED"


class UploadItemStatus(StrEnum):
    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    PARSING = "PARSING"
    NEEDS_OCR = "NEEDS_OCR"
    DEDUPE_REVIEW = "DEDUPE_REVIEW"
    READY = "READY"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DuplicateMatchType(StrEnum):
    EXACT_FILE = "EXACT_FILE"
    CONTACT = "CONTACT"
    SIMILAR_CONTENT = "SIMILAR_CONTENT"


class DuplicateResolution(StrEnum):
    NEEDS_REVIEW = "NEEDS_REVIEW"
    KEEP_BOTH = "KEEP_BOTH"
    LINK_EXISTING = "LINK_EXISTING"
    SKIP = "SKIP"
