from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.models.settings import GlobalSettingsModel, SessionSettingsModel


router = APIRouter()


def _get_or_create_global(db: Session) -> GlobalSettingsModel:
	row = db.get(GlobalSettingsModel, 1)
	if not row:
		row = GlobalSettingsModel(id=1)
		db.add(row)
		db.commit()
		db.refresh(row)
	return row


@router.get("/settings/global")
def get_global_settings(db: Session = Depends(get_session)) -> dict[str, Any]:
	row = _get_or_create_global(db)
	return {
		"temperature": row.temperature,
		"top_p": row.top_p,
		"max_tokens": row.max_tokens,
		"presence_penalty": row.presence_penalty,
		"frequency_penalty": row.frequency_penalty,
	}


@router.post("/settings/global")
def update_global_settings(payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
	row = _get_or_create_global(db)
	# Update only provided keys; ignore unknowns
	for key in ("temperature", "top_p", "max_tokens", "presence_penalty", "frequency_penalty"):
		if key in payload:
			setattr(row, key, payload[key])
	db.add(row)
	db.commit()
	db.refresh(row)
	return {
		"temperature": row.temperature,
		"top_p": row.top_p,
		"max_tokens": row.max_tokens,
		"presence_penalty": row.presence_penalty,
		"frequency_penalty": row.frequency_penalty,
	}


@router.get("/settings/session/{session_id}")
def get_session_settings(session_id: str, db: Session = Depends(get_session)) -> dict[str, Any]:
	global_row = _get_or_create_global(db)
	# Load overrides if exist
	ov = db.get(SessionSettingsModel, session_id)
	overrides = dict(ov.overrides_json) if ov and ov.overrides_json else {}
	# Merge (overrides win over global)
	effective = {
		"temperature": overrides.get("temperature", global_row.temperature),
		"top_p": overrides.get("top_p", global_row.top_p),
		"max_tokens": overrides.get("max_tokens", global_row.max_tokens),
		"presence_penalty": overrides.get("presence_penalty", global_row.presence_penalty),
		"frequency_penalty": overrides.get("frequency_penalty", global_row.frequency_penalty),
	}
	return {"session_id": session_id, "effective": effective, "overrides": overrides}


@router.post("/settings/session/{session_id}")
def update_session_settings(session_id: str, payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
	allowed = {"temperature", "top_p", "max_tokens", "presence_penalty", "frequency_penalty"}
	updates = {k: v for k, v in payload.items() if k in allowed}
	row = db.get(SessionSettingsModel, session_id)
	if not row:
		row = SessionSettingsModel(session_id=session_id, overrides_json={})
	row.overrides_json = {**(row.overrides_json or {}), **updates}
	db.add(row)
	db.commit()
	db.refresh(row)
	return {"session_id": session_id, "overrides": row.overrides_json}


