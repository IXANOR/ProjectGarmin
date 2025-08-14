from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.session import SessionModel, MessageModel


router = APIRouter()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_session(payload: dict, db: Session = Depends(get_session)) -> dict:
    name: Optional[str] = payload.get("name")
    metadata: Optional[dict[str, Any]] = payload.get("metadata")
    session = SessionModel(name=name, metadata_json=metadata)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "name": session.name,
        "created_at": session.created_at.isoformat(),
        "metadata": session.metadata_json or None,
    }


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_session)) -> list[dict]:
    sessions = db.exec(select(SessionModel).order_by(SessionModel.created_at)).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: str, db: Session = Depends(get_session)) -> dict:
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = db.exec(select(MessageModel).where(MessageModel.session_id == session_id).order_by(MessageModel.created_at)).all()
    return {
        "session": {
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "metadata": session.metadata_json or None,
        },
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in msgs
        ],
    }


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_session)) -> None:
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Ensure messages are removed
    db.exec(delete(MessageModel).where(MessageModel.session_id == session_id))
    db.delete(session)
    db.commit()
    return None


