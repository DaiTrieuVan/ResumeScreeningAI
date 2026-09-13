# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.decision_service import DecisionConflictError, DecisionValidationError, append_decision, decision_timeline

router = APIRouter()


class DecisionInput(BaseModel):
    event_type: str
    to_stage: str | None = None
    decision: str | None = None
    reason_code: str | None = Field(None, max_length=80)
    note: str | None = Field(None, max_length=5000)


def event_response(event):
    return {"id": event.id, "application_id": event.application_id, "event_type": event.event_type, "from_stage": event.from_stage, "to_stage": event.to_stage, "decision": event.decision, "reason_code": event.reason_code, "note": event.note, "actor_id": event.actor_id, "before_version": event.before_version, "after_version": event.after_version, "created_at": event.created_at}


@router.get("/applications/{application_id}/decisions")
async def get_decisions(application_id: str, db: AsyncSession = Depends(get_db)):
    return [event_response(event) for event in await decision_timeline(db, application_id)]


@router.post("/applications/{application_id}/decisions", status_code=201)
async def create_decision(application_id: str, payload: DecisionInput, if_match: int = Header(), db: AsyncSession = Depends(get_db)):
    try:
        event = await append_decision(db, application_id, if_match, payload.model_dump())
    except LookupError as error:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except DecisionValidationError as error:
        raise HTTPException(422, detail={"code": "INVALID_DECISION", "message": str(error)}) from error
    except DecisionConflictError as error:
        raise HTTPException(409, detail={"code": "VERSION_CONFLICT", "message": str(error)}) from error
    return event_response(event)
