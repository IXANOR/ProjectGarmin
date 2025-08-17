from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.core.db import get_session
from app.models.settings import GlobalSettingsModel, SessionSettingsModel, SearchSettingsModel


router = APIRouter()


def _get_or_create_global(db: Session) -> GlobalSettingsModel:
	row = db.get(GlobalSettingsModel, 1)
	if not row:
		row = GlobalSettingsModel(id=1)
		db.add(row)
		try:
			db.commit()
		except IntegrityError:
			db.rollback()
			row = db.get(GlobalSettingsModel, 1)  # fetch if created concurrently
		if row is None:
			row = GlobalSettingsModel(id=1)
			db.add(row)
			db.commit()
		db.refresh(row)
	return row


def _get_or_create_search(db: Session) -> SearchSettingsModel:
	row = db.get(SearchSettingsModel, 1)
	if not row:
		row = SearchSettingsModel(id=1)
		db.add(row)
		try:
			db.commit()
		except IntegrityError:
			db.rollback()
			row = db.get(SearchSettingsModel, 1)
		if row is None:
			row = SearchSettingsModel(id=1)
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


@router.get("/settings/search")
def get_search_settings(db: Session = Depends(get_session)) -> dict[str, Any]:
	row = _get_or_create_search(db)
	return {
		"allow_internet_search": bool(row.allow_internet_search),
		"debug_logging": bool(row.debug_logging),
		"has_bing_api_key": bool(row.bing_api_key or ""),
	}


@router.post("/settings/search")
def update_search_settings(payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
	row = _get_or_create_search(db)
	if "allow_internet_search" in payload:
		row.allow_internet_search = bool(payload["allow_internet_search"])
	if "debug_logging" in payload:
		row.debug_logging = bool(payload["debug_logging"])
	# Accept and store bing_api_key if provided
	if "bing_api_key" in payload:
		val = payload["bing_api_key"]
		row.bing_api_key = str(val) if val else None
	db.add(row)
	db.commit()
	db.refresh(row)
	return {
		"allow_internet_search": bool(row.allow_internet_search),
		"debug_logging": bool(row.debug_logging),
		"has_bing_api_key": bool(row.bing_api_key or ""),
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


