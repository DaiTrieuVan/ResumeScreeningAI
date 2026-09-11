from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent
from app.models.candidate_evaluation import CandidateApplication
from app.models.recruiter_enums import PipelineStage
from app.models.recruitment_decision import RecruitmentDecisionEvent


EVENT_TYPES = {"STAGE_CHANGED", "NOTE_ADDED", "HUMAN_DECISION", "SCORE_OVERRIDE"}
HUMAN_DECISIONS = {"ADVANCE", "HOLD", "REJECT", "HIRE"}


class DecisionValidationError(ValueError):
    pass


class DecisionConflictError(RuntimeError):
    pass


async def append_decision(db: AsyncSession, application_id: str, expected_version: int, payload: dict, actor_id: str = "system"):
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise LookupError("Không tìm thấy hồ sơ ứng viên.")
    if application.version != expected_version:
        raise DecisionConflictError(f"Hồ sơ đã thay đổi từ phiên bản {expected_version} sang {application.version}.")
    event_type = payload.get("event_type")
    to_stage = payload.get("to_stage")
    decision = payload.get("decision")
    reason_code = (payload.get("reason_code") or "").strip() or None
    note = (payload.get("note") or "").strip() or None
    if event_type not in EVENT_TYPES:
        raise DecisionValidationError("Loại sự kiện không hợp lệ.")
    if to_stage and to_stage not in {stage.value for stage in PipelineStage}:
        raise DecisionValidationError("Giai đoạn tuyển dụng không hợp lệ.")
    if event_type == "STAGE_CHANGED" and not to_stage:
        raise DecisionValidationError("Cần chọn giai đoạn tiếp theo.")
    if event_type == "NOTE_ADDED" and not note:
        raise DecisionValidationError("Ghi chú không được để trống.")
    if event_type == "HUMAN_DECISION" and decision not in HUMAN_DECISIONS:
        raise DecisionValidationError("Quyết định của recruiter không hợp lệ.")
    if (decision == "REJECT" or to_stage == PipelineStage.REJECTED.value) and not reason_code:
        raise DecisionValidationError("Từ chối ứng viên bắt buộc phải có lý do.")

    before_version = application.version
    from_stage = application.pipeline_stage
    if to_stage:
        application.pipeline_stage = to_stage
    if decision:
        application.human_decision = decision
        application.decision_reason_code = reason_code
    application.version += 1
    event = RecruitmentDecisionEvent(
        application_id=application.id, event_type=event_type, from_stage=from_stage,
        to_stage=to_stage, decision=decision, reason_code=reason_code, note=note,
        actor_id=actor_id, before_version=before_version, after_version=application.version,
    )
    db.add(event)
    db.add(AuditEvent(action=event_type, resource_type="CandidateApplication", resource_id=application.id, actor_id=actor_id, resource_version=application.version, metadata_json={"from_stage": from_stage, "to_stage": to_stage, "decision": decision, "reason_code": reason_code}))
    await db.flush()
    return event


async def decision_timeline(db: AsyncSession, application_id: str):
    return (await db.scalars(select(RecruitmentDecisionEvent).where(RecruitmentDecisionEvent.application_id == application_id).order_by(RecruitmentDecisionEvent.created_at.desc(), RecruitmentDecisionEvent.id.desc()))).all()
