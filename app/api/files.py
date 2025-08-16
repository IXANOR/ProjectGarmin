from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.file import FileModel
from app.services.rag import RagService


router = APIRouter()


@router.post("/files", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(default=None),
    db: Session = Depends(get_session),
) -> dict:
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    data = await file.read()
    size_bytes = len(data)
    record = FileModel(name=file.filename, session_id=session_id, size_bytes=size_bytes)
    db.add(record)
    db.commit()
    db.refresh(record)

    # Process PDF: parse -> chunk -> embed -> persist
    rag = RagService()
    try:
        text = rag.parse_pdf(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF uploaded")
    chunks = rag.chunk_text(text, chunk_size=320, overlap=40)
    rag.persist_chunks(file_id=record.id, session_id=session_id, chunks=chunks)

    return {
        "id": record.id,
        "name": record.name,
        "session_id": record.session_id,
        "size_bytes": record.size_bytes,
        "created_at": record.created_at.isoformat(),
    }


@router.get("/files")
def list_files(session_id: Optional[str] = None, db: Session = Depends(get_session)) -> list[dict]:
    query = select(FileModel).order_by(FileModel.created_at)
    files = db.exec(query).all()
    if session_id:
        # Include global (NULL) and session-specific
        filtered = [f for f in files if f.session_id in (None, session_id)]
    else:
        filtered = files
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


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: str, db: Session = Depends(get_session)) -> Response:
    rec = db.get(FileModel, file_id)
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    # Remove vectors from Chroma by metadata filter
    rag = RagService()
    rag._collection.delete(where={"file_id": file_id})
    # Delete DB record
    db.delete(rec)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


