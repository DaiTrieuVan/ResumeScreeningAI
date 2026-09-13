# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate_evaluation import CandidateApplication, CriterionResult, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume
from app.models.screening_criteria import ScreeningCriteriaSet


class ComparisonConflictError(RuntimeError):
    pass


async def compare_candidates(db: AsyncSession, job_id: str, application_ids: list[str], criteria_set_id: str):
    criteria_set = await db.scalar(select(ScreeningCriteriaSet).options(selectinload(ScreeningCriteriaSet.criteria)).where(ScreeningCriteriaSet.id == criteria_set_id, ScreeningCriteriaSet.job_id == job_id))
    if not criteria_set:
        raise LookupError("Không tìm thấy phiên bản tiêu chí cho vị trí này.")
    candidates = []
    evaluations = {}
    for application_id in application_ids:
        application = await db.get(CandidateApplication, application_id)
        if not application or application.job_id != job_id:
            raise LookupError(f"Không tìm thấy hồ sơ {application_id} trong vị trí này.")
        evaluation = await db.scalar(select(ScreeningEvaluation).options(selectinload(ScreeningEvaluation.criterion_results).selectinload(CriterionResult.evidence)).where(ScreeningEvaluation.application_id == application_id, ScreeningEvaluation.criteria_set_id == criteria_set_id).order_by(ScreeningEvaluation.evaluated_at.desc()).limit(1))
        if not evaluation:
            raise ComparisonConflictError("Một hoặc nhiều ứng viên chưa được đánh giá theo cùng phiên bản tiêu chí.")
        resume = await db.get(CandidateResume, application.resume_id)
        candidates.append({"application_id": application.id, "candidate_name": resume.parsed_name or resume.file_name, "pipeline_stage": application.pipeline_stage, "overall_score": evaluation.overall_score, "mandatory_gate": evaluation.mandatory_gate, "human_decision": application.human_decision})
        evaluations[application_id] = {result.criterion_id: result for result in evaluation.criterion_results}

    criteria = []
    for criterion in sorted(criteria_set.criteria, key=lambda item: item.sort_order):
        result_map = {}
        for application_id in application_ids:
            result = evaluations[application_id].get(criterion.id)
            result_map[application_id] = None if not result else {"result": result.result, "confidence": result.confidence, "explanation": result.explanation, "evidence": [{"excerpt": evidence.excerpt, "confidence": evidence.confidence, "page_number": evidence.page_number} for evidence in result.evidence]}
        criteria.append({"criterion_id": criterion.id, "label": criterion.label, "importance": criterion.importance, "results": result_map})
    return {"criteria_set_id": criteria_set_id, "criteria_version": criteria_set.version_number, "candidates": candidates, "criteria": criteria}
