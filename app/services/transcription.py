from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from types import SimpleNamespace
import tempfile

try:  # pragma: no cover - allow tests to run without faster_whisper installed
	from faster_whisper import WhisperModel  # type: ignore

	class _FWNamespace:
		WhisperModel = WhisperModel  # type: ignore
except Exception:  # pragma: no cover - fallback for test envs
	class _PlaceholderWhisperModel:  # allows monkeypatching of .transcribe without import
		def __init__(self, *args, **kwargs) -> None:  # accept any args
			pass

		def transcribe(self, *args, **kwargs):
			raise RuntimeError("faster-whisper is not installed")

	faster_whisper = SimpleNamespace(WhisperModel=_PlaceholderWhisperModel)  # type: ignore
else:
	faster_whisper = _FWNamespace()  # type: ignore


class AudioTranscriptionService:
	def __init__(self, model_size: Optional[str] = None) -> None:
		if model_size is None:
			from app.core.config import get_whisper_model_size
			model_size = get_whisper_model_size()
		self._model_size = model_size
		self._model = None  # lazy init to avoid heavy load unless needed

	def _ensure_model(self) -> None:
		if self._model is None:
			# Prefer int8/float16 if GPU/CPU available; leave defaults to library
			self._model = faster_whisper.WhisperModel(self._model_size)

	def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> List[Dict[str, Any]]:
		self._ensure_model()
		# Write to a temp file to satisfy library expectations
		with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
			tmp.write(audio_bytes)
			tmp.flush()
			segments, _info = self._model.transcribe(tmp.name, language=language)
		out: List[Dict[str, Any]] = []
		for seg in segments:
			text = getattr(seg, "text", "") or ""
			start = float(getattr(seg, "start", 0.0))
			end = float(getattr(seg, "end", 0.0))
			out.append({"text": text.strip(), "start": start, "end": end})
		return out


