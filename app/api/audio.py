from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.config import (
	get_supported_audio_suffixes,
	get_audio_max_file_size_bytes,
)
from app.models.file import FileModel
from app.services.rag import RagService
from app.services.transcription import AudioTranscriptionService


router = APIRouter()


SUPPORTED_EXTS = get_supported_audio_suffixes()


@router.post("/audio", status_code=status.HTTP_201_CREATED)
async def upload_audio(
	file: UploadFile = File(...),
	session_id: Optional[str] = Form(default=None),
	db: Session = Depends(get_session),
) -> dict:
	suffix = Path(file.filename).suffix.lower()
	if suffix not in SUPPORTED_EXTS:
		raise HTTPException(status_code=400, detail="Unsupported audio format")

	data = await file.read()
	size_bytes = len(data)
	if size_bytes > get_audio_max_file_size_bytes():
		raise HTTPException(status_code=400, detail="Audio file too large")

	# Store original audio to disk for debugging/playback
	base = Path("data") / "uploads" / "audio"
	base.mkdir(parents=True, exist_ok=True)

	record = FileModel(name=file.filename, session_id=session_id, size_bytes=size_bytes)
	db.add(record)
	db.commit()
	db.refresh(record)

	# Save original with id prefix to avoid collisions
	dest = base / f"{record.id}{suffix}"
	dest.write_bytes(data)

	# Transcribe -> chunk -> embed -> persist with source_type=audio and timings
	transcriber = AudioTranscriptionService()
	try:
		segments = transcriber.transcribe(data)
	except Exception:
		raise HTTPException(status_code=400, detail="Invalid or unreadable audio uploaded")

	full_text = " ".join(s.get("text", "") for s in segments).strip()
	rag = RagService()
	chunks = rag.chunk_text(full_text, chunk_size=320, overlap=40)

	# Approximate timings per chunk as overall bounds for now
	start_time = float(segments[0]["start"]) if segments else 0.0
	end_time = float(segments[-1]["end"]) if segments else 0.0
	metadatas = []
	for i in range(len(chunks)):
		m = {
			"file_id": record.id,
			"session_id": (session_id if session_id is not None else "GLOBAL"),
			"chunk_index": i,
			"source_type": "audio",
			"start_time": start_time,
			"end_time": end_time,
		}
		metadatas.append(m)

	rag.persist_documents(documents=chunks, metadatas=metadatas)

	return {
		"id": record.id,
		"name": record.name,
		"session_id": record.session_id,
		"size_bytes": record.size_bytes,
		"created_at": record.created_at.isoformat(),
	}


@router.get("/audio")
def list_audio(session_id: Optional[str] = None, db: Session = Depends(get_session)) -> list[dict]:
	# Reuse files table: filter by name extension
	items = db.exec(select(FileModel).order_by(FileModel.created_at)).all()

	def _is_audio(name: str) -> bool:
		return Path(name).suffix.lower() in SUPPORTED_EXTS

	filtered = [f for f in items if _is_audio(f.name)]
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


@router.delete("/audio/{audio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audio(audio_id: str, db: Session = Depends(get_session)) -> Response:
	rec = db.get(FileModel, audio_id)
	if not rec:
		raise HTTPException(status_code=404, detail="Audio not found")
	# Delete vectors
	rag = RagService()
	rag._collection.delete(where={"file_id": audio_id})
	# Delete original file if present
	base = Path("data") / "uploads" / "audio"
	for ext in SUPPORTED_EXTS:
		p = base / f"{audio_id}{ext}"
		if p.exists():
			try:
				p.unlink()
			except Exception:
				pass
	# Delete DB record
	db.delete(rec)
	db.commit()
	return Response(status_code=status.HTTP_204_NO_CONTENT)


