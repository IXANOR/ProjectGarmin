from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple

from sqlmodel import Session, select

from app.models.settings import PersonalityProfileModel, SessionPersonalityOverrideModel
from app.models.session import MessageModel


ALLOWED_FORMALITY = {"formal", "neutral", "casual"}
ALLOWED_HUMOR = {"none", "moderate", "frequent"}
ALLOWED_LENGTH = {"concise", "normal", "elaborate"}
ALLOWED_DETAIL = {"low", "medium", "high"}
ALLOWED_STYLE = {"technical", "creative", "mixed"}


DEFAULT_PROFILE = {
	"formality": "neutral",
	"humor": "none",
	"swearing": False,
	"length": "normal",
	"detail": "medium",
	"proactivity": False,
	"style": "mixed",
}


PREDEFINED_PROFILES = {
	"formal": {
		"formality": "formal",
		"humor": "none",
		"swearing": False,
		"length": "normal",
		"detail": "high",
		"proactivity": False,
		"style": "technical",
	},
	"friendly": {
		"formality": "casual",
		"humor": "moderate",
		"swearing": False,
		"length": "normal",
		"detail": "medium",
		"proactivity": True,
		"style": "mixed",
	},
	"sarcastic": {
		"formality": "casual",
		"humor": "frequent",
		"swearing": False,
		"length": "concise",
		"detail": "low",
		"proactivity": False,
		"style": "creative",
	},
	"jarvis": {
		"formality": "formal",
		"humor": "moderate",
		"swearing": False,
		"length": "concise",
		"detail": "high",
		"proactivity": True,
		"style": "technical",
	},
}


class PersonalityService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def _get_or_create(self) -> PersonalityProfileModel:
		row = self.db.get(PersonalityProfileModel, 1)
		if not row:
			row = PersonalityProfileModel(id=1, last_updated=datetime.utcnow(), **DEFAULT_PROFILE)
			self.db.add(row)
			self.db.commit()
			self.db.refresh(row)
		return row

	def get_current(self) -> Dict[str, Any]:
		row = self._get_or_create()
		return {
			"formality": row.formality,
			"humor": row.humor,
			"swearing": bool(row.swearing),
			"length": row.length,
			"detail": row.detail,
			"proactivity": bool(row.proactivity),
			"style": row.style,
			"last_updated": row.last_updated.isoformat(),
		}

	def get_effective_for_session(self, session_id: str) -> Dict[str, Any]:
		base = self.get_current()
		ov = self.db.get(SessionPersonalityOverrideModel, session_id)
		overrides = dict(ov.overrides_json) if ov and ov.overrides_json else {}
		return {**base, **overrides}

	def update_partial(self, payload: Dict[str, Any]) -> Dict[str, Any]:
		row = self._get_or_create()
		updates: Dict[str, Any] = {}
		if "formality" in payload and payload["formality"] in ALLOWED_FORMALITY:
			updates["formality"] = payload["formality"]
		if "humor" in payload and payload["humor"] in ALLOWED_HUMOR:
			updates["humor"] = payload["humor"]
		if "swearing" in payload:
			updates["swearing"] = bool(payload["swearing"])
		if "length" in payload and payload["length"] in ALLOWED_LENGTH:
			updates["length"] = payload["length"]
		if "detail" in payload and payload["detail"] in ALLOWED_DETAIL:
			updates["detail"] = payload["detail"]
		if "proactivity" in payload:
			updates["proactivity"] = bool(payload["proactivity"])
		if "style" in payload and payload["style"] in ALLOWED_STYLE:
			updates["style"] = payload["style"]
		for k, v in updates.items():
			setattr(row, k, v)
		row.last_updated = datetime.utcnow()
		self.db.add(row)
		self.db.commit()
		self.db.refresh(row)
		return self.get_current()

	def apply_profile(self, name: str) -> Dict[str, Any]:
		preset = PREDEFINED_PROFILES.get(name.lower())
		if not preset:
			return self.get_current()
		return self.update_partial(preset)

	def get_session_overrides(self, session_id: str) -> Dict[str, Any]:
		row = self.db.get(SessionPersonalityOverrideModel, session_id)
		return dict(row.overrides_json) if row and row.overrides_json else {}

	def update_session_overrides(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
		allowed_keys = {
			"formality",
			"humor",
			"swearing",
			"length",
			"detail",
			"proactivity",
			"style",
		}
		updates = {k: v for k, v in payload.items() if k in allowed_keys}
		row = self.db.get(SessionPersonalityOverrideModel, session_id)
		if not row:
			row = SessionPersonalityOverrideModel(session_id=session_id, overrides_json={})
		row.overrides_json = {**(row.overrides_json or {}), **updates}
		self.db.add(row)
		self.db.commit()
		self.db.refresh(row)
		return dict(row.overrides_json)

	def detect_from_messages(self, session_id: str, max_messages: int = 20) -> Dict[str, Any]:
		"""Heuristic detection of user style from recent messages.

		Looks at the last N user messages in the session and infers adjustments.
		This is intentionally lightweight to keep overhead minimal.
		"""
		rows: List[MessageModel] = self.db.exec(
			select(MessageModel)
			.where(MessageModel.session_id == session_id)
			.order_by(MessageModel.id.desc())
			.limit(max_messages)
		).all()
		user_texts = [r.content for r in rows if r.role == "user" and isinstance(r.content, str)]
		joined = "\n".join(user_texts).lower()
		updates: Dict[str, Any] = {}
		# Formality cues
		if any(w in joined for w in ("dear ", "regards", "sincerely", "please advise")):
			updates["formality"] = "formal"
		elif any(w in joined for w in ("hey", "yo", "what's up", "sup", "thx", "pls")):
			updates["formality"] = "casual"
		# Humor detection
		if any(w in joined for w in ("lol", "haha", "😀", ":)")) or joined.count("!") >= 3:
			updates["humor"] = "frequent"
		# Swearing detection (very basic)
		if any(w in joined for w in ("fuck", "shit", "damn")):
			updates["swearing"] = True
		# Length preference
		if any(w in joined for w in ("tl;dr", "short pls", "brief", "concise")):
			updates["length"] = "concise"
		elif any(w in joined for w in ("explain in detail", "step by step", "elaborate")):
			updates["length"] = "elaborate"
		# Detail preference
		if any(w in joined for w in ("details", "in-depth", "why")):
			updates["detail"] = "high"
		# Proactivity cues
		if any(w in joined for w in ("suggest", "recommend", "what else", "next steps")):
			updates["proactivity"] = True
		# Style cues
		if any(w in joined for w in ("api", "stacktrace", "compile", "sql", "runtime")):
			updates["style"] = "technical"
		elif any(w in joined for w in ("story", "metaphor", "imagine", "poem")):
			updates["style"] = "creative"
		return updates

	def adapt_global_profile(self, session_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
		"""Detect from recent messages and persist any changes to the global profile.

		Returns (before, after) profile dicts. If no change, before==after.
		"""
		before = self.get_current()
		updates = self.detect_from_messages(session_id)
		if not updates:
			return before, before
		merged = {**before, **updates}
		# Only keep allowed enums/bools
		cleaned = {}
		if merged.get("formality") in ALLOWED_FORMALITY:
			cleaned["formality"] = merged["formality"]
		if merged.get("humor") in ALLOWED_HUMOR:
			cleaned["humor"] = merged["humor"]
		if "swearing" in merged:
			cleaned["swearing"] = bool(merged["swearing"])
		if merged.get("length") in ALLOWED_LENGTH:
			cleaned["length"] = merged["length"]
		if merged.get("detail") in ALLOWED_DETAIL:
			cleaned["detail"] = merged["detail"]
		if "proactivity" in merged:
			cleaned["proactivity"] = bool(merged["proactivity"])
		if merged.get("style") in ALLOWED_STYLE:
			cleaned["style"] = merged["style"]
		if not cleaned:
			return before, before
		after = self.update_partial(cleaned)
		return before, after

	def build_system_instructions(self, profile: Dict[str, Any]) -> str:
		"""Construct a compact instruction snippet representing the personality.

		This can be injected into the model's system prompt by the chat pipeline.
		"""
		return (
			f"Tone: {profile['formality']}; Humor: {profile['humor']}; Swearing: {'allowed' if profile['swearing'] else 'disallowed'}; "
			f"Length: {profile['length']}; Detail: {profile['detail']}; Proactivity: {profile['proactivity']}; Style: {profile['style']}"
		)


