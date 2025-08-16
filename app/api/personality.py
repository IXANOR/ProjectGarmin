from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.services.personality_service import PersonalityService, PREDEFINED_PROFILES


router = APIRouter()


@router.get("/personality")
def get_personality(db: Session = Depends(get_session)) -> dict[str, Any]:
	ps = PersonalityService(db)
	return ps.get_current()


@router.post("/personality")
def update_personality(payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
	ps = PersonalityService(db)
	return ps.update_partial(payload or {})


@router.put("/personality")
def set_personality_profile(payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
	ps = PersonalityService(db)
	name = (payload or {}).get("profile")
	if not isinstance(name, str):
		return ps.get_current()
	return ps.apply_profile(name)


@router.get("/personality/profiles")
def list_predefined_profiles() -> dict[str, Any]:
	return {"profiles": list(PREDEFINED_PROFILES.keys())}


@router.get("/personality/session/{session_id}")
def get_personality_for_session(session_id: str, db: Session = Depends(get_session)) -> dict[str, Any]:
	ps = PersonalityService(db)
	return {
		"session_id": session_id,
		"effective": ps.get_effective_for_session(session_id),
		"overrides": ps.get_session_overrides(session_id),
	}


@router.post("/personality/session/{session_id}")
def update_personality_for_session(session_id: str, payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
	ps = PersonalityService(db)
	overrides = ps.update_session_overrides(session_id, payload or {})
	return {"session_id": session_id, "overrides": overrides}


