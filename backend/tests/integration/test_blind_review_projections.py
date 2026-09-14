# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.exports import router as exports_router
from app.api.recruiter import router as recruiter_router
from app.core.database import Base, get_db
from app.models.candidate_evaluation import CandidateApplication, CriterionResult, EvidenceSnippet, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume
from app.models.final_release import ReviewPrivacyPolicy
from app.models.job_posting import JobPosting
from app.models.screening_criteria import Criterion, ScreeningCriteriaSet
from app.models.screening_result import ScreeningResult
import app.models.recruiter_productivity  # noqa: F401
import app.models.recruitment_decision  # noqa: F401
import app.models.upload_batch  # noqa: F401


@pytest.mark.asyncio
async def test_blind_mode_masks_list_detail_comparison_evidence_filename_and_export(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'blind-projections.db'}")
    sessions = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with sessions() as db:
        job = JobPosting(title="Privacy matrix", required_skills=["Python"])
        db.add(job)
        await db.flush()
        policy = ReviewPrivacyPolicy(job_id=job.id, mode="BLIND", masked_fields=["name", "email", "phone", "file_name", "employer", "school"])
        db.add(policy)
        criteria_set = ScreeningCriteriaSet(job_id=job.id, version_number=1, name="v1", status="PUBLISHED", scoring_weights={"skills": 1}, criteria=[])
        criterion = Criterion(category="SKILL", importance="MANDATORY", label="Python", operator="CONTAINS_ANY", expected_value=["Python"], weight=1, sort_order=0)
        criteria_set.criteria.append(criterion)
        db.add(criteria_set)
        await db.flush()

        application_ids = []
        for index in range(2):
            resume = CandidateResume(
                job_id=job.id,
                file_name=f"Nguyen-An-{index}.pdf",
                file_path="unused",
                file_size_bytes=10,
                raw_text=f"Nguyen An {index} an{index}@example.com 090123456{index} Python",
                parsed_name=f"Nguyen An {index}",
                parsed_email=f"an{index}@example.com",
                parsed_phone=f"090123456{index}",
                work_history=[{"employer": "Private Corp", "description": f"Email an{index}@example.com"}],
                education=[{"school": "Private University"}],
            )
            db.add(resume)
            await db.flush()
            application = CandidateApplication(job_id=job.id, resume_id=resume.id, pipeline_stage="SHORTLISTED")
            db.add(application)
            await db.flush()
            application_ids.append(application.id)
            evaluation = ScreeningEvaluation(application_id=application.id, criteria_set_id=criteria_set.id, component_scores={"skills": 90}, overall_score=90-index, mandatory_gate="PASSED", input_fingerprint=f"blind-{index}", criterion_results=[])
            result = CriterionResult(criterion_id=criterion.id, label="Python", importance="MANDATORY", result="MET", score=100, confidence=.95, explanation=f"Nguyen An {index} contact an{index}@example.com", evidence=[])
            result.evidence.append(EvidenceSnippet(resume_id=resume.id, start_offset=0, end_offset=6, excerpt=f"Call 090123456{index} or an{index}@example.com", polarity="SUPPORTS", confidence=.9))
            evaluation.criterion_results.append(result)
            db.add(evaluation)
            db.add(ScreeningResult(job_id=job.id, resume_id=resume.id, overall_score=90-index, skills_sub_score=90, experience_sub_score=80, education_sub_score=70, recruiter_status="SHORTLISTED", strengths_summary=[f"Nguyen An {index}"], gaps_summary=[f"Call 090123456{index}"], ai_reasoning=f"Email an{index}@example.com"))
        await db.commit()

    async def override_db():
        async with sessions() as db:
            yield db
            await db.commit()

    app = FastAPI()
    app.include_router(recruiter_router, prefix="/api")
    app.include_router(exports_router, prefix="/api")
    app.dependency_overrides[get_db] = override_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        listing = await client.get(f"/api/recruiter/jobs/{job.id}/candidates")
        detail = await client.get(f"/api/recruiter/applications/{application_ids[0]}")
        comparison = await client.post(f"/api/recruiter/jobs/{job.id}/comparisons", json={"application_ids": application_ids, "criteria_set_id": criteria_set.id})
        exported = await client.get(f"/api/exports/csv/{job.id}?status_filter=ALL")

    assert listing.status_code == detail.status_code == comparison.status_code == exported.status_code == 200
    combined = "\n".join([
        listing.text,
        detail.text,
        comparison.text,
        exported.content.decode("utf-8-sig"),
    ])
    for secret in ("Nguyen An", "example.com", "090123456", "Private Corp", "Private University"):
        assert secret not in combined
    assert listing.json()["privacy_mode"] == "BLIND"
    assert detail.json()["resume_available"] is False
    assert comparison.json()["privacy_mode"] == "BLIND"
    assert "Ứng viên" in combined
    await engine.dispose()
