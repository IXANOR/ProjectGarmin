from __future__ import annotations

from typing import Any, Dict, Optional
import re

from sqlmodel import Session, select

from app.models.settings import (
    ThemeSettingsModel,
    SessionThemeSettingsModel,
    ThemePresetModel,
)


BUILT_IN_PRESETS: dict[str, dict[str, str]] = {
    "light": {"background_color": "#ffffff", "text_color": "#111111", "panel_color": "#ffffff", "border_color": "#e5e7eb", "font_type": "system"},
    # Dark: use a dark gray background instead of pure black, with even darker panel for contrast
    "dark": {"background_color": "#1f2937", "text_color": "#e5e7eb", "panel_color": "#111827", "border_color": "#374151", "font_type": "system"},
}


ALLOWED_KEYS = {"background_color", "text_color", "panel_color", "border_color", "font_type", "preset_name"}
ALLOWED_FONTS = {
    "system",
    "arial",
    "helvetica",
    "times_new_roman",
    "georgia",
    "courier_new",
    "consolas",
    "fira_code",
    "roboto",
    "inter",
}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class ThemeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_or_create(self) -> ThemeSettingsModel:
        row = self.db.get(ThemeSettingsModel, 1)
        if not row:
            row = ThemeSettingsModel(id=1)
            self.db.add(row)
            try:
                # Import here to avoid hard dependency at module import time
                from sqlalchemy.exc import IntegrityError  # type: ignore
                try:
                    self.db.commit()
                except IntegrityError:
                    self.db.rollback()
                    row = self.db.get(ThemeSettingsModel, 1)  # type: ignore[assignment]
            except Exception:
                # If we cannot import or handle, do a best-effort commit
                try:
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                    row = self.db.get(ThemeSettingsModel, 1)  # type: ignore[assignment]
            if row is None:
                row = ThemeSettingsModel(id=1)
                self.db.add(row)
                self.db.commit()
            self.db.refresh(row)
        return row

    def get_current(self) -> Dict[str, Any]:
        row = self._get_or_create()
        return {
            "background_color": row.background_color,
            "text_color": row.text_color,
            "panel_color": row.panel_color,
            "border_color": getattr(row, "border_color", "#e5e7eb"),
            "font_type": row.font_type,
            "preset_name": row.preset_name,
        }

    def update_partial(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = self._get_or_create()
        for key, value in payload.items():
            if key not in ALLOWED_KEYS:
                continue
            if key in {"background_color", "text_color", "panel_color", "border_color"}:
                if isinstance(value, str) and HEX_RE.match(value):
                    setattr(row, key, value)
                continue
            if key == "font_type":
                if isinstance(value, str) and value in ALLOWED_FONTS:
                    row.font_type = value
                continue
            if key == "preset_name" and isinstance(value, str):
                row.preset_name = value
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self.get_current()

    def _get_preset_values(self, name: str) -> Dict[str, str] | None:
        name_norm = name.lower().strip()
        if name_norm in BUILT_IN_PRESETS:
            return BUILT_IN_PRESETS[name_norm]
        custom = self.db.get(ThemePresetModel, name)
        if not custom:
            return None
        return {
            "background_color": custom.background_color,
            "text_color": custom.text_color,
            "panel_color": custom.panel_color,
            "border_color": getattr(custom, "border_color", "#e5e7eb"),
            "font_type": custom.font_type,
        }

    def apply_preset(self, name: str) -> Dict[str, Any]:
        name_norm = name.lower().strip()
        row = self._get_or_create()
        preset = self._get_preset_values(name_norm)
        if not preset:
            return self.get_current()
        row.background_color = preset["background_color"]
        row.text_color = preset["text_color"]
        row.panel_color = preset.get("panel_color", row.panel_color)
        if "border_color" in preset:
            setattr(row, "border_color", preset["border_color"])  # support migration
        row.font_type = preset["font_type"]
        row.preset_name = name_norm
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self.get_current()

    def get_effective_for_session(self, session_id: str) -> Dict[str, Any]:
        base = self.get_current()
        ov = self.db.get(SessionThemeSettingsModel, session_id)
        overrides = dict(ov.overrides_json) if ov and ov.overrides_json else {}
        return {**base, **overrides}

    def get_session_overrides(self, session_id: str) -> Dict[str, Any]:
        ov = self.db.get(SessionThemeSettingsModel, session_id)
        return dict(ov.overrides_json) if ov and ov.overrides_json else {}

    def update_session_overrides(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Allow applying a preset to session overrides
        if isinstance(payload.get("preset"), str):
            preset = self._get_preset_values(payload["preset"]) or {}
        else:
            preset = {}
        raw_updates = {k: v for k, v in payload.items() if k in {"background_color", "text_color", "font_type"}}
        updates: Dict[str, Any] = {}
        # Validate hex colors
        if isinstance(raw_updates.get("background_color"), str) and HEX_RE.match(raw_updates["background_color"]):
            updates["background_color"] = raw_updates["background_color"]
        if isinstance(raw_updates.get("text_color"), str) and HEX_RE.match(raw_updates["text_color"]):
            updates["text_color"] = raw_updates["text_color"]
        if isinstance(raw_updates.get("panel_color"), str) and HEX_RE.match(raw_updates["panel_color"]):
            updates["panel_color"] = raw_updates["panel_color"]
        if isinstance(raw_updates.get("border_color"), str) and HEX_RE.match(raw_updates["border_color"]):
            updates["border_color"] = raw_updates["border_color"]
        # Validate font
        if isinstance(raw_updates.get("font_type"), str) and raw_updates["font_type"] in ALLOWED_FONTS:
            updates["font_type"] = raw_updates["font_type"]
        # Merge preset values last so they can override unspecified fields
        updates = {**updates, **preset}
        row = self.db.get(SessionThemeSettingsModel, session_id)
        if not row:
            row = SessionThemeSettingsModel(session_id=session_id, overrides_json={})
        row.overrides_json = {**(row.overrides_json or {}), **updates}
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return dict(row.overrides_json or {})

    def list_presets(self) -> Dict[str, Any]:
        custom = self.db.exec(select(ThemePresetModel)).all()
        return {
            "built_in": [{"name": k, **v} for k, v in BUILT_IN_PRESETS.items()],
            "custom": [
                {
                    "name": p.name,
                    "background_color": p.background_color,
                    "text_color": p.text_color,
                    "panel_color": p.panel_color,
                    "border_color": getattr(p, "border_color", "#e5e7eb"),
                    "font_type": p.font_type,
                }
                for p in custom
            ],
        }

    def save_custom_preset(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        name = payload.get("name")
        bg = payload.get("background_color")
        fg = payload.get("text_color")
        pc = payload.get("panel_color")
        bc = payload.get("border_color")
        font = payload.get("font_type")
        # Validate name
        if not isinstance(name, str):
            return {"ok": False}
        name_norm = name.strip().lower()
        if name_norm in BUILT_IN_PRESETS:
            return {"ok": False}
        if not (1 <= len(name) <= 32) or not re.match(r"^[A-Za-z0-9_\- ]+$", name):
            return {"ok": False}
        # If some fields missing, take from current theme
        current = self._get_or_create()
        if bg is None:
            bg = current.background_color
        if fg is None:
            fg = current.text_color
        if pc is None:
            pc = getattr(current, "panel_color", "#ffffff")
        if bc is None:
            bc = getattr(current, "border_color", "#e5e7eb")
        if font is None:
            font = current.font_type
        # Validate colors and font
        if not (isinstance(bg, str) and HEX_RE.match(bg)):
            return {"ok": False}
        if not (isinstance(fg, str) and HEX_RE.match(fg)):
            return {"ok": False}
        if not (isinstance(pc, str) and HEX_RE.match(pc)):
            return {"ok": False}
        if not (isinstance(bc, str) and HEX_RE.match(bc)):
            return {"ok": False}
        if not (isinstance(font, str) and font in ALLOWED_FONTS):
            return {"ok": False}
        existing = self.db.get(ThemePresetModel, name)
        if existing:
            existing.background_color = bg
            existing.text_color = fg
            existing.panel_color = pc
            setattr(existing, "border_color", bc)
            existing.font_type = font
            self.db.add(existing)
        else:
            self.db.add(ThemePresetModel(name=name, background_color=bg, text_color=fg, panel_color=pc, border_color=bc, font_type=font))
        self.db.commit()
        return {"ok": True}

    def delete_custom_preset(self, name: str) -> Dict[str, Any]:
        """Delete a custom preset by name; built-ins cannot be deleted."""
        if not isinstance(name, str):
            return {"ok": False}
        name_norm = name.strip().lower()
        if name_norm in BUILT_IN_PRESETS:
            return {"ok": False}
        row = self.db.get(ThemePresetModel, name)
        if not row:
            return {"ok": False}
        self.db.delete(row)
        self.db.commit()
        return {"ok": True}


