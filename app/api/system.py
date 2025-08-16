from __future__ import annotations

from fastapi import APIRouter

from app.services.system_monitor import get_system_monitor


router = APIRouter()


@router.get("/system/usage")
def get_system_usage() -> dict:
    monitor = get_system_monitor()
    return monitor.get_usage()


@router.get("/system/settings")
def get_system_settings() -> dict:
    monitor = get_system_monitor()
    return monitor.get_settings()


@router.post("/system/settings")
def update_system_settings(payload: dict) -> dict:
    monitor = get_system_monitor()
    mode = payload.get("mode")
    debug_logging = payload.get("debug_logging")
    return monitor.update_settings(mode=mode, debug_logging=debug_logging)


