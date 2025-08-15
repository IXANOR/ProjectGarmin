from __future__ import annotations

from io import BytesIO
from typing import Optional
from types import SimpleNamespace

try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover - fallback for test envs without pytesseract installed
    def _missing(*args, **kwargs):
        raise RuntimeError("pytesseract is not installed")

    pytesseract = SimpleNamespace(image_to_string=_missing)  # type: ignore


class OcrService:
    def __init__(self, lang: Optional[str] = None) -> None:
        if lang is None:
            from app.core.config import get_ocr_language
            lang = get_ocr_language()
        self._lang = lang

    def extract_text(self, image_bytes: bytes) -> str:
        from PIL import Image  # lazy import to avoid hard dependency at module import time
        with Image.open(BytesIO(image_bytes)) as img:
            txt = pytesseract.image_to_string(img, lang=self._lang)
        return (txt or "").strip()


