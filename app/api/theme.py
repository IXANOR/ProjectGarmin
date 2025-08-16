from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.services.theme_service import ThemeService


router = APIRouter()


@router.get("/theme")
def get_theme(db: Session = Depends(get_session)) -> dict[str, Any]:
    ts = ThemeService(db)
    return ts.get_current()


@router.post("/theme")
def update_theme(payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
    ts = ThemeService(db)
    return ts.update_partial(payload or {})


@router.put("/theme")
def set_theme_preset(payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
    ts = ThemeService(db)
    name = (payload or {}).get("preset")
    if not isinstance(name, str):
        return ts.get_current()
    return ts.apply_preset(name)


@router.get("/theme/session/{session_id}")
def get_theme_for_session(session_id: str, db: Session = Depends(get_session)) -> dict[str, Any]:
    ts = ThemeService(db)
    return {
        "session_id": session_id,
        "effective": ts.get_effective_for_session(session_id),
        "overrides": ts.get_session_overrides(session_id),
    }


@router.put("/theme/session/{session_id}")
def update_theme_for_session(session_id: str, payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
    ts = ThemeService(db)
    overrides = ts.update_session_overrides(session_id, payload or {})
    return {"session_id": session_id, "overrides": overrides}


@router.get("/theme/presets")
def list_presets(db: Session = Depends(get_session)) -> dict[str, Any]:
    ts = ThemeService(db)
    return ts.list_presets()


@router.post("/theme/presets")
def save_custom_preset(payload: dict[str, Any], db: Session = Depends(get_session)) -> dict[str, Any]:
    ts = ThemeService(db)
    return ts.save_custom_preset(payload or {})


