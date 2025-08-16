from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.models.session import SessionModel
from app.services.context_manager import ContextManager


router = APIRouter()


@router.get("/context/summary")
def get_context_summary(session_id: str, db: Session = Depends(get_session)) -> dict:
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    cm = ContextManager(db)
    summary = cm.get_last_summary(session_id)
    knowledge = cm.list_knowledge(session_id, limit=5)
    return {
        "session_id": session_id,
        "summary": summary,
        "knowledge": [
            {
                "id": k.id,
                "key": k.key,
                "value": k.value,
                "source_message_id": k.source_message_id,
            }
            for k in knowledge
        ],
    }


@router.post("/context/restore")
def restore_trimmed(payload: dict, db: Session = Depends(get_session)) -> dict:
    session_id: Optional[str] = payload.get("session_id")
    count: int = int(payload.get("count") or 0)
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    cm = ContextManager(db)
    restored = cm.restore_trimmed(session_id, count)
    return {"restored": restored}


