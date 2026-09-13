# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job_posting import JobPosting
from app.models.recruiter_enums import CriteriaSetStatus
from app.models.screening_criteria import Criterion, ScreeningCriteriaSet
from app.schemas.screening_criteria import CriteriaSetInput


class CriteriaValidationError(ValueError):
    def __init__(self, message: str, field_errors: dict[str, str] | None = None):
        super().__init__(message)
        self.field_errors = field_errors or {}


def validate_scoring_weights(weights: dict[str, float]) -> None:
    total = sum(weights.values())
    if any(value < 0 or value > 1 for value in weights.values()):
        raise CriteriaValidationError(
            "Trọng số không hợp lệ.",
            {"scoring_weights": "Mỗi trọng số phải nằm trong khoảng 0–100%."},
        )
    if abs(total - 1.0) > 0.0001:
        percent = round(total * 100, 2)
        percent_label = int(percent) if percent.is_integer() else percent
        raise CriteriaValidationError(
            "Tổng trọng số phải bằng 100%.",
            {"scoring_weights": f"Tổng trọng số phải bằng 100% (hiện tại {percent_label}%)."},
        )


async def _get_job(db: AsyncSession, job_id: str) -> JobPosting:
    job = await db.get(JobPosting, job_id)
    if not job:
        raise LookupError(f"Không tìm thấy vị trí tuyển dụng {job_id}.")
    return job


async def create_criteria_draft(
    db: AsyncSession,
    job_id: str,
    data: CriteriaSetInput,
    actor_id: str = "system",
) -> ScreeningCriteriaSet:
    await _get_job(db, job_id)
    maximum = await db.scalar(
        select(func.max(ScreeningCriteriaSet.version_number)).where(
            ScreeningCriteriaSet.job_id == job_id
        )
    )
    criteria_set = ScreeningCriteriaSet(
        job_id=job_id,
        version_number=(maximum or 0) + 1,
        name=data.name,
        scoring_weights=data.scoring_weights,
        created_by=actor_id,
    )
    criteria_set.criteria = []
    for index, criterion in enumerate(data.criteria):
        values = criterion.model_dump()
        if values["sort_order"] == 0 and index > 0:
            values["sort_order"] = index
        criteria_set.criteria.append(Criterion(**values))
    db.add(criteria_set)
    await db.flush()
    return criteria_set


async def list_criteria_sets(db: AsyncSession, job_id: str) -> list[ScreeningCriteriaSet]:
    await ensure_legacy_criteria_set(db, job_id)
    result = await db.execute(
        select(ScreeningCriteriaSet)
        .options(selectinload(ScreeningCriteriaSet.criteria))
        .where(ScreeningCriteriaSet.job_id == job_id)
        .order_by(ScreeningCriteriaSet.version_number.desc())
    )
    return list(result.scalars().unique().all())


async def publish_criteria_set(
    db: AsyncSession,
    criteria_set_id: str,
    expected_job_version: int,
    actor_id: str = "system",
) -> ScreeningCriteriaSet:
    result = await db.execute(
        select(ScreeningCriteriaSet)
        .options(selectinload(ScreeningCriteriaSet.criteria))
        .where(ScreeningCriteriaSet.id == criteria_set_id)
    )
    criteria_set = result.scalar_one_or_none()
    if not criteria_set:
        raise LookupError(f"Không tìm thấy bộ tiêu chí {criteria_set_id}.")
    if criteria_set.status != CriteriaSetStatus.DRAFT.value:
        raise CriteriaValidationError("Chỉ có thể publish một bản nháp.")

    validate_scoring_weights(criteria_set.scoring_weights)
    job = await _get_job(db, criteria_set.job_id)
    if job.version != expected_job_version:
        raise RuntimeError("Vị trí đã được cập nhật ở một phiên khác.")

    if job.active_criteria_set_id:
        previous = await db.get(ScreeningCriteriaSet, job.active_criteria_set_id)
        if previous and previous.status == CriteriaSetStatus.PUBLISHED.value:
            previous.status = CriteriaSetStatus.RETIRED.value

    criteria_set.status = CriteriaSetStatus.PUBLISHED.value
    criteria_set.published_by = actor_id
    criteria_set.published_at = datetime.utcnow()
    job.active_criteria_set_id = criteria_set.id
    job.version += 1
    await db.flush()
    return criteria_set


async def ensure_legacy_criteria_set(
    db: AsyncSession, job_id: str
) -> ScreeningCriteriaSet | None:
    job = await _get_job(db, job_id)
    existing = await db.scalar(
        select(ScreeningCriteriaSet).where(ScreeningCriteriaSet.job_id == job_id).limit(1)
    )
    if existing:
        return existing

    weights = {
        "skills": job.weight_skills,
        "experience": job.weight_experience,
        "education": job.weight_education,
    }
    # Legacy rows may contain imprecise floats. Normalize only the generated v1 snapshot.
    total = sum(weights.values()) or 1.0
    weights = {key: value / total for key, value in weights.items()}
    criteria_set = ScreeningCriteriaSet(
        job_id=job.id,
        version_number=1,
        name="Tiêu chí ban đầu",
        status=CriteriaSetStatus.PUBLISHED.value,
        scoring_weights=weights,
        created_by="migration",
        published_by="migration",
        published_at=datetime.utcnow(),
    )
    order = 0
    for skill in job.required_skills or []:
        criteria_set.criteria.append(
            Criterion(
                category="SKILL",
                importance="MANDATORY",
                label=skill,
                operator="CONTAINS_ANY",
                expected_value=[skill],
                weight=0.0,
                sort_order=order,
            )
        )
        order += 1
    if job.min_years_experience:
        criteria_set.criteria.append(
            Criterion(
                category="EXPERIENCE",
                importance="MANDATORY",
                label=f"Tối thiểu {job.min_years_experience} năm kinh nghiệm",
                operator="MIN_VALUE",
                expected_value=job.min_years_experience,
                weight=0.0,
                sort_order=order,
            )
        )
        order += 1
    if job.required_education:
        criteria_set.criteria.append(
            Criterion(
                category="EDUCATION",
                importance="PREFERRED",
                label=job.required_education,
                operator="EQUALS",
                expected_value=job.required_education,
                weight=0.0,
                sort_order=order,
            )
        )
    db.add(criteria_set)
    await db.flush()
    job.active_criteria_set_id = criteria_set.id
    return criteria_set


async def get_official_scoring_config(
    db: AsyncSession, job: JobPosting
) -> tuple[str | None, dict[str, float]]:
    if job.active_criteria_set_id:
        active = await db.get(ScreeningCriteriaSet, job.active_criteria_set_id)
        if active and active.status == CriteriaSetStatus.PUBLISHED.value:
            return active.id, dict(active.scoring_weights)
    return None, {
        "skills": job.weight_skills,
        "experience": job.weight_experience,
        "education": job.weight_education,
    }
