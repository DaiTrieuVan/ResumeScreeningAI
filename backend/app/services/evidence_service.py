# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import hashlib
import json
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate_evaluation import (
    CandidateApplication,
    CriterionResult,
    EvidenceSnippet,
    ScreeningEvaluation,
)
from app.models.candidate_resume import CandidateResume
from app.models.recruiter_enums import CriterionOutcome, EvaluationKind, MandatoryGate, PipelineStage
from app.models.screening_criteria import Criterion, ScreeningCriteriaSet
from app.models.screening_result import ScreeningResult


def find_text_evidence(text: str, terms: list[str], context: int = 90) -> dict | None:
    folded = text.casefold()
    for term in sorted((term.strip() for term in terms if term), key=len, reverse=True):
        start = folded.find(term.casefold())
        if start >= 0:
            end = start + len(term)
            excerpt_start = max(0, start - context)
            excerpt_end = min(len(text), end + context)
            return {
                "start_offset": start,
                "end_offset": end,
                "excerpt": text[excerpt_start:excerpt_end].strip(),
                "confidence": 0.95,
            }
    return None


def evaluate_criterion(criterion: Criterion, resume: CandidateResume) -> tuple[str, float, str, dict | None]:
    text = resume.raw_text or ""
    expected = criterion.expected_value
    terms = expected if isinstance(expected, list) else [str(expected)]

    if criterion.category == "EXPERIENCE" and criterion.operator == "MIN_VALUE":
        years = [(int(match.group(1)), match) for match in re.finditer(r"(\d+)\s*(?:\+\s*)?(?:năm|years?)", text, re.IGNORECASE)]
        if not years:
            return CriterionOutcome.UNKNOWN.value, 0.25, "Chưa tìm thấy số năm kinh nghiệm có thể kiểm chứng.", None
        best_years, match = max(years, key=lambda pair: pair[0])
        required = float(expected)
        excerpt_start = max(0, match.start() - 90)
        excerpt_end = min(len(text), match.end() + 90)
        evidence = {
            "start_offset": match.start(), "end_offset": match.end(),
            "excerpt": text[excerpt_start:excerpt_end].strip(), "confidence": 0.82,
        }
        if best_years >= required:
            return CriterionOutcome.MET.value, 0.82, f"CV thể hiện khoảng {best_years} năm kinh nghiệm.", evidence
        return CriterionOutcome.NOT_MET.value, 0.82, f"CV thể hiện {best_years} năm, thấp hơn mức {required:g} năm.", evidence

    evidence = find_text_evidence(text, terms)
    if evidence:
        return CriterionOutcome.MET.value, evidence["confidence"], "Tìm thấy bằng chứng trực tiếp trong CV.", evidence
    return CriterionOutcome.UNKNOWN.value, 0.2, "Không tìm thấy bằng chứng trực tiếp trong CV.", None


def evaluation_fingerprint(screening: ScreeningResult, resume: CandidateResume) -> str:
    payload = {
        "criteria_set_id": screening.criteria_set_id,
        "resume": hashlib.sha256((resume.raw_text or "").encode("utf-8")).hexdigest(),
        "scores": [screening.skills_sub_score, screening.experience_sub_score, screening.education_sub_score, screening.overall_score],
        "reasoning": screening.ai_reasoning,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


async def get_or_create_application(
    db: AsyncSession, screening: ScreeningResult
) -> CandidateApplication:
    application = await db.scalar(
        select(CandidateApplication).where(
            CandidateApplication.job_id == screening.job_id,
            CandidateApplication.resume_id == screening.resume_id,
        )
    )
    if application:
        return application
    stage_map = {
        "SHORTLISTED": PipelineStage.SHORTLISTED.value,
        "UNDER_REVIEW": PipelineStage.RECRUITER_REVIEW.value,
        "REJECTED": PipelineStage.REJECTED.value,
    }
    application = CandidateApplication(
        job_id=screening.job_id,
        resume_id=screening.resume_id,
        pipeline_stage=stage_map.get(screening.recruiter_status, PipelineStage.AI_ANALYZED.value),
        ai_recommendation="ADVANCE" if (screening.overall_score or 0) >= 70 else "REVIEW",
    )
    db.add(application)
    await db.flush()
    return application


async def sync_screening_evaluation(
    db: AsyncSession, screening: ScreeningResult, resume: CandidateResume
) -> tuple[CandidateApplication, ScreeningEvaluation]:
    application = await get_or_create_application(db, screening)
    fingerprint = evaluation_fingerprint(screening, resume)
    existing = await db.scalar(
        select(ScreeningEvaluation).where(
            ScreeningEvaluation.application_id == application.id,
            ScreeningEvaluation.input_fingerprint == fingerprint,
        )
    )
    if existing:
        return application, existing

    criteria_set = None
    if screening.criteria_set_id:
        criteria_set = await db.scalar(
            select(ScreeningCriteriaSet)
            .options(selectinload(ScreeningCriteriaSet.criteria))
            .where(ScreeningCriteriaSet.id == screening.criteria_set_id)
        )

    evaluation = ScreeningEvaluation(
        application_id=application.id,
        criteria_set_id=screening.criteria_set_id if criteria_set else None,
        screening_result_id=screening.id,
        evaluation_kind=screening.evaluation_kind or EvaluationKind.LEGACY.value,
        component_scores={
            "skills": screening.skills_sub_score or 0.0,
            "experience": screening.experience_sub_score or 0.0,
            "education": screening.education_sub_score or 0.0,
        },
        overall_score=screening.overall_score or 0.0,
        input_fingerprint=fingerprint,
        evidence_status="UNAVAILABLE_LEGACY" if not criteria_set else "PARTIAL",
        criterion_results=[],
    )

    outcomes = []
    evidence_count = 0
    if criteria_set:
        for criterion in criteria_set.criteria:
            outcome, confidence, explanation, evidence = evaluate_criterion(criterion, resume)
            outcomes.append((criterion.importance, outcome))
            result = CriterionResult(
                criterion_id=criterion.id,
                label=criterion.label,
                importance=criterion.importance,
                result=outcome,
                score=100.0 if outcome == CriterionOutcome.MET.value else None,
                confidence=confidence,
                explanation=explanation,
                needs_manual_review=outcome == CriterionOutcome.UNKNOWN.value or confidence < 0.6,
                evidence=[],
            )
            if evidence:
                evidence_count += 1
                result.evidence.append(EvidenceSnippet(
                    resume_id=resume.id,
                    start_offset=evidence["start_offset"],
                    end_offset=evidence["end_offset"],
                    excerpt=evidence["excerpt"],
                    polarity="SUPPORTS" if outcome == CriterionOutcome.MET.value else "CONTRADICTS",
                    confidence=evidence["confidence"],
                ))
            evaluation.criterion_results.append(result)

    mandatory = [outcome for importance, outcome in outcomes if importance == "MANDATORY"]
    if CriterionOutcome.NOT_MET.value in mandatory:
        evaluation.mandatory_gate = MandatoryGate.FAILED.value
    elif CriterionOutcome.UNKNOWN.value in mandatory or not mandatory:
        evaluation.mandatory_gate = MandatoryGate.NEEDS_REVIEW.value
    else:
        evaluation.mandatory_gate = MandatoryGate.PASSED.value
    if criteria_set and evidence_count == len(criteria_set.criteria):
        evaluation.evidence_status = "AVAILABLE"

    db.add(evaluation)
    await db.flush()
    return application, evaluation


async def load_candidate_detail(db: AsyncSession, application_id: str):
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise LookupError(f"Không tìm thấy hồ sơ ứng tuyển {application_id}.")
    resume = await db.get(CandidateResume, application.resume_id)
    evaluation = await db.scalar(
        select(ScreeningEvaluation)
        .options(selectinload(ScreeningEvaluation.criterion_results).selectinload(CriterionResult.evidence))
        .where(ScreeningEvaluation.application_id == application.id)
        .order_by(ScreeningEvaluation.evaluated_at.desc())
        .limit(1)
    )
    return application, resume, evaluation
