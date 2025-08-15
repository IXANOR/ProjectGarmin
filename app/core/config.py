from __future__ import annotations

import os
from pathlib import Path
from typing import Set


def get_supported_image_suffixes() -> Set[str]:
    raw = os.getenv("SUPPORTED_IMAGE_FORMATS")
    if raw:
        # Expect comma-separated like ".png,.jpg,.jpeg"
        vals = [s.strip().lower() for s in raw.split(",") if s.strip()]
        return set(vals)
    return {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}


def get_ocr_language() -> str:
    return os.getenv("OCR_LANG", "eng")


def get_images_max_file_size_bytes() -> int:
    # Default 10 MB
    mb = float(os.getenv("IMAGES_MAX_FILE_SIZE_MB", "10"))
    return int(mb * 1024 * 1024)


def get_chroma_path() -> Path:
    return Path(os.getenv("CHROMA_PATH") or Path("data") / "chroma")


def get_supported_audio_suffixes() -> Set[str]:
    raw = os.getenv("SUPPORTED_AUDIO_FORMATS")
    if raw:
        vals = [s.strip().lower() for s in raw.split(",") if s.strip()]
        return set(vals)
    return {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def get_audio_max_file_size_bytes() -> int:
    # Default 20 MB
    mb = float(os.getenv("AUDIO_MAX_FILE_SIZE_MB", "20"))
    return int(mb * 1024 * 1024)


def get_whisper_model_size() -> str:
    return os.getenv("WHISPER_MODEL_SIZE", "base")


