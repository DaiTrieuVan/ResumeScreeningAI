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
from app.models.final_release import ResumePage
from app.models.recruiter_enums import CriterionOutcome, EvaluationKind, MandatoryGate, PipelineStage
from app.models.screening_criteria import Criterion, ScreeningCriteriaSet
from app.models.screening_result import ScreeningResult
from app.services.scoring_service import SCORING_VERSION, calculate_verified_score


def _page_value(page, key: str):
    return page.get(key) if isinstance(page, dict) else getattr(page, key)


def _with_source_location(evidence: dict, pages: list | None) -> dict:
    evidence.update({"page_number": None, "resume_page_id": None, "source_method": "LEGACY_UNKNOWN"})
    for page in pages or []:
        if _page_value(page, "normalized_start_offset") <= evidence["start_offset"] < _page_value(page, "normalized_end_offset"):
            evidence.update({
                "page_number": _page_value(page, "page_number"),
                "resume_page_id": None if isinstance(page, dict) else page.id,
                "source_method": _page_value(page, "extraction_method"),
            })
            break
    return evidence


def find_text_evidence(text: str, terms: list[str], context: int = 90, pages: list | None = None) -> dict | None:
    folded = text.casefold()
    for term in sorted((term.strip() for term in terms if term), key=len, reverse=True):
        start = folded.find(term.casefold())
        if start >= 0:
            end = start + len(term)
            excerpt_start = max(0, start - context)
            excerpt_end = min(len(text), end + context)
            return _with_source_location({
                "start_offset": start,
                "end_offset": end,
                "excerpt": text[excerpt_start:excerpt_end].strip(),
                "confidence": 0.95,
            }, pages)
    return None


def _expected_terms(expected: object, operator: str) -> list[str]:
    terms = expected if isinstance(expected, list) else [str(expected)]
    if operator in {"CONTAINS_ANY", "CONTAINS_ALL"} and len(terms) == 1:
        split_terms = [part.strip() for part in re.split(r"[/|,;]", terms[0]) if part.strip()]
        if len(split_terms) > 1:
            return split_terms
    return [str(term).strip() for term in terms if str(term).strip()]


def _date_range_evidence(text: str, required_years: float, pages: list | None) -> tuple[str, float, str, dict | None] | None:
    pattern = re.compile(
        r"(?P<start_month>\d{1,2})/(?P<start_year>\d{4})\s*(?:to|[-–—])\s*"
        r"(?P<end_month>\d{1,2})/(?P<end_year>\d{4})",
        re.IGNORECASE,
    )
    valid_ranges: list[tuple[int, re.Match]] = []
    for match in pattern.finditer(text):
        start_month = int(match.group("start_month"))
        end_month = int(match.group("end_month"))
        if not 1 <= start_month <= 12 or not 1 <= end_month <= 12:
            continue
        start_index = int(match.group("start_year")) * 12 + start_month
        end_index = int(match.group("end_year")) * 12 + end_month
        if end_index >= start_index:
            valid_ranges.append((end_index - start_index, match))
    if not valid_ranges:
        return None

    months, match = max(valid_ranges, key=lambda pair: pair[0])
    years = months / 12.0
    evidence = _with_source_location({
        "start_offset": match.start(),
        "end_offset": match.end(),
        "excerpt": text[max(0, match.start() - 90):min(len(text), match.end() + 90)].strip(),
        "confidence": 0.88,
    }, pages)
    if years >= required_years:
        return CriterionOutcome.MET.value, 0.88, f"CV có khoảng thời gian làm việc liên tục khoảng {years:.1f} năm.", evidence
    return CriterionOutcome.NOT_MET.value, 0.88, f"Khoảng thời gian kiểm chứng được là {years:.1f} năm, thấp hơn mức {required_years:g} năm.", evidence


def evaluate_criterion(criterion: Criterion, resume: CandidateResume, pages: list | None = None) -> tuple[str, float, str, dict | None]:
    text = resume.raw_text or ""
    expected = criterion.expected_value
    terms = _expected_terms(expected, criterion.operator)

    if criterion.category == "EXPERIENCE" and criterion.operator == "MIN_VALUE":
        years = [(int(match.group(1)), match) for match in re.finditer(r"(\d+)\s*(?:\+\s*)?(?:năm|years?)", text, re.IGNORECASE)]
        if not years:
            date_range_result = _date_range_evidence(text, float(expected), pages)
            if date_range_result:
                return date_range_result
            return CriterionOutcome.UNKNOWN.value, 0.25, "Chưa tìm thấy số năm kinh nghiệm có thể kiểm chứng.", None
        best_years, match = max(years, key=lambda pair: pair[0])
        required = float(expected)
        excerpt_start = max(0, match.start() - 90)
        excerpt_end = min(len(text), match.end() + 90)
        evidence = _with_source_location({
            "start_offset": match.start(), "end_offset": match.end(),
            "excerpt": text[excerpt_start:excerpt_end].strip(), "confidence": 0.82,
        }, pages)
        if best_years >= required:
            return CriterionOutcome.MET.value, 0.82, f"CV thể hiện khoảng {best_years} năm kinh nghiệm.", evidence
        return CriterionOutcome.NOT_MET.value, 0.82, f"CV thể hiện {best_years} năm, thấp hơn mức {required:g} năm.", evidence

    matches = [find_text_evidence(text, [term], pages=pages) for term in terms]
    found = [evidence for evidence in matches if evidence]
    if criterion.operator == "CONTAINS_ALL" and found and len(found) < len(terms):
        return CriterionOutcome.PARTIAL.value, 0.8, f"Tìm thấy {len(found)}/{len(terms)} thành phần yêu cầu.", found[0]
    evidence = found[0] if found and (criterion.operator != "CONTAINS_ALL" or len(found) == len(terms)) else None
    if evidence:
        return CriterionOutcome.MET.value, evidence["confidence"], "Tìm thấy bằng chứng trực tiếp trong CV.", evidence
    return CriterionOutcome.UNKNOWN.value, 0.2, "Không tìm thấy bằng chứng trực tiếp trong CV.", None


def evaluation_fingerprint(screening: ScreeningResult, resume: CandidateResume) -> str:
    payload = {
        "scoring_version": SCORING_VERSION,
        "criteria_set_id": screening.criteria_set_id,
        "resume": hashlib.sha256((resume.raw_text or "").encode("utf-8")).hexdigest(),
        "score_override": screening.score_override,
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
    criteria_set = None
    if screening.criteria_set_id:
        criteria_set = await db.scalar(
            select(ScreeningCriteriaSet)
            .options(selectinload(ScreeningCriteriaSet.criteria))
            .where(ScreeningCriteriaSet.id == screening.criteria_set_id)
        )

    pages = (await db.execute(select(ResumePage).where(ResumePage.resume_id == resume.id).order_by(ResumePage.page_number))).scalars().all()
    outcomes = []
    evaluated_items: list[dict] = []
    if criteria_set:
        for criterion in criteria_set.criteria:
            outcome, confidence, explanation, evidence = evaluate_criterion(criterion, resume, pages)
            outcomes.append((criterion.importance, outcome))
            evaluated_items.append({
                "criterion": criterion,
                "category": criterion.category,
                "weight": criterion.weight,
                "outcome": outcome,
                "confidence": confidence,
                "explanation": explanation,
                "evidence": evidence,
                "score": 100.0 if outcome == CriterionOutcome.MET.value else (50.0 if outcome == CriterionOutcome.PARTIAL.value else None),
            })

    mandatory = [outcome for importance, outcome in outcomes if importance == "MANDATORY"]
    if CriterionOutcome.NOT_MET.value in mandatory:
        mandatory_gate = MandatoryGate.FAILED.value
    elif CriterionOutcome.UNKNOWN.value in mandatory or CriterionOutcome.PARTIAL.value in mandatory or not mandatory:
        mandatory_gate = MandatoryGate.NEEDS_REVIEW.value
    else:
        mandatory_gate = MandatoryGate.PASSED.value

    if criteria_set:
        verified = calculate_verified_score([
            {
                "category": item["category"], "weight": item["weight"],
                "result": item["outcome"], "score": item["score"],
            }
            for item in evaluated_items
        ], dict(criteria_set.scoring_weights))
        screening.skills_sub_score = verified.component_scores.get("skills", 0.0)
        screening.experience_sub_score = verified.component_scores.get("experience", 0.0)
        screening.education_sub_score = verified.component_scores.get("education", 0.0)
        screening.overall_score = verified.overall_score
        component_scores = verified.component_scores
        maximum_possible_score = verified.maximum_possible_score
        evidence_coverage = verified.evidence_coverage
        if evidence_coverage >= 100.0:
            evidence_status = "AVAILABLE"
        elif evidence_coverage > 0.0:
            evidence_status = "PARTIAL"
        else:
            evidence_status = "UNAVAILABLE"
        scoring_version = SCORING_VERSION
    else:
        component_scores = {
            "skills": screening.skills_sub_score or 0.0,
            "experience": screening.experience_sub_score or 0.0,
            "education": screening.education_sub_score or 0.0,
        }
        maximum_possible_score = screening.overall_score or 0.0
        evidence_coverage = 0.0
        evidence_status = "UNAVAILABLE_LEGACY"
        scoring_version = "legacy"

    application.ai_recommendation = (
        "ADVANCE"
        if mandatory_gate == MandatoryGate.PASSED.value and (screening.overall_score or 0.0) >= 70.0
        else "REVIEW"
    )
    fingerprint = evaluation_fingerprint(screening, resume)
    existing = await db.scalar(
        select(ScreeningEvaluation).where(
            ScreeningEvaluation.application_id == application.id,
            ScreeningEvaluation.input_fingerprint == fingerprint,
        )
    )
    if existing:
        return application, existing

    evaluation = ScreeningEvaluation(
        application_id=application.id,
        criteria_set_id=screening.criteria_set_id if criteria_set else None,
        screening_result_id=screening.id,
        evaluation_kind=screening.evaluation_kind or EvaluationKind.LEGACY.value,
        component_scores=component_scores,
        overall_score=screening.overall_score or 0.0,
        maximum_possible_score=maximum_possible_score,
        evidence_coverage=evidence_coverage,
        scoring_version=scoring_version,
        mandatory_gate=mandatory_gate,
        input_fingerprint=fingerprint,
        evidence_status=evidence_status,
        criterion_results=[],
    )

    for item in evaluated_items:
        criterion = item["criterion"]
        outcome = item["outcome"]
        evidence = item["evidence"]
        result = CriterionResult(
            criterion_id=criterion.id,
            label=criterion.label,
            importance=criterion.importance,
            result=outcome,
            score=item["score"],
            confidence=item["confidence"],
            explanation=item["explanation"],
            needs_manual_review=outcome in {CriterionOutcome.UNKNOWN.value, CriterionOutcome.PARTIAL.value} or item["confidence"] < 0.6,
            evidence=[],
        )
        if evidence:
            result.evidence.append(EvidenceSnippet(
                resume_id=resume.id,
                page_number=evidence["page_number"],
                resume_page_id=evidence["resume_page_id"],
                start_offset=evidence["start_offset"],
                end_offset=evidence["end_offset"],
                excerpt=evidence["excerpt"],
                polarity="CONTRADICTS" if outcome == CriterionOutcome.NOT_MET.value else "SUPPORTS",
                confidence=evidence["confidence"],
                source_method=evidence["source_method"],
            ))
        evaluation.criterion_results.append(result)

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
