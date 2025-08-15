from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.config import get_supported_image_suffixes, get_images_max_file_size_bytes
from app.models.file import FileModel
from app.services.rag import RagService
from app.services.ocr import OcrService


router = APIRouter()


SUPPORTED_EXTS = get_supported_image_suffixes()


@router.post("/images", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(default=None),
    db: Session = Depends(get_session),
) -> dict:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTS:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    data = await file.read()
    size_bytes = len(data)
    if size_bytes > get_images_max_file_size_bytes():
        raise HTTPException(status_code=400, detail="Image too large")
    # Store original image to disk for debugging/preview
    base = Path("data") / "uploads" / "images"
    base.mkdir(parents=True, exist_ok=True)

    record = FileModel(name=file.filename, session_id=session_id, size_bytes=size_bytes)
    db.add(record)
    db.commit()
    db.refresh(record)

    # Save original with id prefix to avoid collisions
    dest = base / f"{record.id}{suffix}"
    dest.write_bytes(data)

    # OCR -> chunk -> embed -> persist with source_type=image
    ocr = OcrService()
    try:
        text = ocr.extract_text(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or unreadable image uploaded")
    rag = RagService()
    chunks = rag.chunk_text(text, chunk_size=500, overlap=50)
    rag.persist_chunks(file_id=record.id, session_id=session_id, chunks=chunks, source_type="image")

    return {
        "id": record.id,
        "name": record.name,
        "session_id": record.session_id,
        "size_bytes": record.size_bytes,
        "created_at": record.created_at.isoformat(),
    }


@router.get("/images")
def list_images(session_id: Optional[str] = None, db: Session = Depends(get_session)) -> list[dict]:
    # Reuse files table: filter by name extension
    items = db.exec(select(FileModel).order_by(FileModel.created_at)).all()
    def _is_image(name: str) -> bool:
        return Path(name).suffix.lower() in SUPPORTED_EXTS
    filtered = [f for f in items if _is_image(f.name)]
    if session_id:
        filtered = [f for f in filtered if f.session_id in (None, session_id)]
    return [
        {
            "id": f.id,
            "name": f.name,
            "session_id": f.session_id,
            "size_bytes": f.size_bytes,
            "created_at": f.created_at.isoformat(),
        }
        for f in filtered
    ]


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: str, db: Session = Depends(get_session)) -> Response:
    rec = db.get(FileModel, image_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Image not found")
    # Delete vectors
    rag = RagService()
    rag._collection.delete(where={"file_id": image_id})
    # Delete original file if present
    base = Path("data") / "uploads" / "images"
    for ext in SUPPORTED_EXTS:
        p = base / f"{image_id}{ext}"
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass
    # Delete DB record
    db.delete(rec)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


