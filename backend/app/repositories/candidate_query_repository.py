from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_evaluation import CandidateApplication, ScreeningEvaluation
from app.models.candidate_resume import CandidateResume


SORTS = {
    "score_desc": ScreeningEvaluation.overall_score.desc(),
    "score_asc": ScreeningEvaluation.overall_score.asc(),
    "received_desc": CandidateApplication.received_at.desc(),
    "risk_desc": ScreeningEvaluation.mandatory_gate.desc(),
}


async def query_candidates(db: AsyncSession, job_id: str, *, q=None, stages=None, mandatory_gate=None, min_score=None, skills=None, sort="score_desc", page=1, page_size=25):
    latest_evaluation = (select(ScreeningEvaluation.id).where(ScreeningEvaluation.application_id == CandidateApplication.id).order_by(ScreeningEvaluation.evaluated_at.desc()).limit(1).correlate(CandidateApplication).scalar_subquery())
    filters = [CandidateApplication.job_id == job_id]
    if q:
        like = f"%{q.strip()}%"
        filters.append(or_(CandidateResume.parsed_name.ilike(like), CandidateResume.parsed_email.ilike(like), CandidateResume.raw_text.ilike(like)))
    if stages:
        filters.append(CandidateApplication.pipeline_stage.in_(stages))
    if mandatory_gate:
        filters.append(ScreeningEvaluation.mandatory_gate == mandatory_gate)
    if min_score is not None:
        filters.append(ScreeningEvaluation.overall_score >= min_score)
    for skill in skills or []:
        filters.append(CandidateResume.raw_text.ilike(f"%{skill}%"))
    base = select(CandidateApplication, CandidateResume, ScreeningEvaluation).join(CandidateResume, CandidateResume.id == CandidateApplication.resume_id).outerjoin(ScreeningEvaluation, ScreeningEvaluation.id == latest_evaluation).where(and_(*filters))
    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = (await db.execute(base.order_by(SORTS.get(sort, SORTS["score_desc"]), CandidateApplication.id).offset((page - 1) * page_size).limit(page_size))).all()
    return rows, total
