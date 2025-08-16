from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response, Query
from fastapi.responses import FileResponse
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

    # Save original PDF for future reprocessing
    pdf_dir = Path("data") / "uploads" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    (pdf_dir / f"{record.id}.pdf").write_bytes(data)

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
def list_files(
    session_id: Optional[str] = None,
    type: Optional[str] = Query(default=None, pattern="^(pdf|image|audio)$"),
    sort: Optional[str] = Query(default=None, pattern="^(name|date)$"),
    order: Optional[str] = Query(default="asc", pattern="^(asc|desc)$"),
    q: Optional[str] = None,
    db: Session = Depends(get_session),
) -> list[dict]:
    query = select(FileModel)
    files = db.exec(query).all()

    def _match_type(name: str, t: Optional[str]) -> bool:
        if t is None:
            return True
        suffix = Path(name).suffix.lower()
        if t == "pdf":
            return suffix == ".pdf"
        if t == "image":
            from app.core.config import get_supported_image_suffixes
            return suffix in get_supported_image_suffixes()
        if t == "audio":
            from app.core.config import get_supported_audio_suffixes
            return suffix in get_supported_audio_suffixes()
        return True

    # Filter soft-deleted out
    files = [f for f in files if not f.is_soft_deleted]
    # Session filter includes global
    if session_id:
        files = [f for f in files if f.session_id in (None, session_id)]
    # Simple name search
    if q:
        q_lower = q.lower()
        files = [f for f in files if q_lower in f.name.lower()]
    # Type filter
    files = [f for f in files if _match_type(f.name, type)]
    # Sort
    if sort == "name":
        files.sort(key=lambda f: (f.name.lower()))
    else:
        files.sort(key=lambda f: f.created_at)
    if order == "desc":
        files.reverse()

    # Build chunk counts by querying chroma metadata for file_id
    out: List[dict] = []
    rag = RagService()
    for f in files:
        try:
            got = rag._collection.get(where={"file_id": f.id})
            ids0 = got.get("ids", [])
            if isinstance(ids0, list) and ids0 and isinstance(ids0[0], list):
                ids0 = ids0[0]
            chunk_count = len(ids0)
        except Exception:
            chunk_count = 0

        rec = {
            "id": f.id,
            "name": f.name,
            "session_id": f.session_id,
            "size_bytes": f.size_bytes,
            "created_at": f.created_at.isoformat(),
            "chunk_count": chunk_count,
        }
        # For audio add transcription_language if present in any metadata
        if Path(f.name).suffix.lower() in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
            try:
                got2 = rag._collection.get(where={"file_id": f.id}, include=["metadatas"])  # type: ignore[arg-type]
                metas = got2.get("metadatas", [])
                if isinstance(metas, list) and metas and isinstance(metas[0], list):
                    metas = metas[0]
                lang = None
                for m in metas:
                    cand = m.get("transcription_language") or m.get("language")
                    if cand:
                        lang = cand
                        break
                rec["transcription_language"] = lang
            except Exception:
                rec["transcription_language"] = None
        out.append(rec)
    return out


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: str, mode: str = Query(default="hard", pattern="^(soft|hard)$"), db: Session = Depends(get_session)) -> Response:
    rec = db.get(FileModel, file_id)
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    rag = RagService()
    if mode == "soft":
        # Mark as soft-deleted to hide from listings but keep vectors/originals
        rec.is_soft_deleted = True
        db.add(rec)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    # Hard delete: remove vectors and DB record
    try:
        rag._collection.delete(where={"file_id": file_id})
    except Exception:
        pass
    # Remove stored originals if present (pdf/image/audio)
    try:
        suffix = Path(rec.name).suffix.lower()
        if suffix == ".pdf":
            pdf_path = Path("data") / "uploads" / "pdfs" / f"{file_id}.pdf"
            if pdf_path.exists():
                pdf_path.unlink()
        elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
            base = Path("data") / "uploads" / "images"
            for ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
                p = base / f"{file_id}{ext}"
                if p.exists():
                    p.unlink(missing_ok=True)  # type: ignore[arg-type]
        elif suffix in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
            base = Path("data") / "uploads" / "audio"
            for ext in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
                p = base / f"{file_id}{ext}"
                if p.exists():
                    p.unlink(missing_ok=True)  # type: ignore[arg-type]
    except Exception:
        pass
    db.delete(rec)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/files/upload", status_code=status.HTTP_201_CREATED)
async def multi_upload(files: list[UploadFile] = File(...), session_id: Optional[str] = Form(default=None), db: Session = Depends(get_session)) -> list[dict]:
    created: list[dict] = []
    for uf in files:
        suffix = Path(uf.filename).suffix.lower()
        if suffix == ".pdf":
            # Reuse upload_file logic
            data = await upload_file(file=uf, session_id=session_id, db=db)
            created.append(data)
        elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
            # route to images.upload_image
            from app.api.images import upload_image
            data = await upload_image(file=uf, session_id=session_id, db=db)
            created.append(data)
        elif suffix in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
            from app.api.audio import upload_audio
            data = await upload_audio(file=uf, session_id=session_id, db=db)
            created.append(data)
        else:
            # skip unsupported file silently for queue robustness
            continue
    return created


@router.post("/files/{file_id}/reassign")
def reassign_file(file_id: str, payload: dict, db: Session = Depends(get_session)) -> dict:
    new_session_id = payload.get("session_id")
    rec = db.get(FileModel, file_id)
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    rec.session_id = new_session_id
    db.add(rec)
    db.commit()

    # Update vector metadata session_id
    rag = RagService()
    try:
        got = rag._collection.get(where={"file_id": file_id})  # returns ids, documents, metadatas
        ids = got.get("ids", [])
        documents = got.get("documents", [])
        metadatas = got.get("metadatas", [])
        if ids and isinstance(ids[0], list):
            ids = ids[0]
            documents = documents[0]
            metadatas = metadatas[0]
        if ids:
            # delete then re-add with updated metadatas and fresh embeddings
            rag._collection.delete(ids=ids)
            for m in metadatas:
                m["session_id"] = new_session_id if new_session_id is not None else "GLOBAL"
            try:
                embeddings = rag._embedder.embed(documents)  # type: ignore[attr-defined]
            except Exception:
                embeddings = None
            if embeddings is not None:
                rag._collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
            else:
                rag._collection.add(ids=ids, documents=documents, metadatas=metadatas)
    except Exception:
        pass

    return {"id": rec.id, "session_id": rec.session_id}


@router.post("/files/{file_id}/reprocess")
def reprocess_file(file_id: str, db: Session = Depends(get_session)) -> dict:
    rec = db.get(FileModel, file_id)
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    rag = RagService()
    suffix = Path(rec.name).suffix.lower()
    if suffix == ".pdf":
        # Rebuild vectors from stored original if available
        pdf_path = Path("data") / "uploads" / "pdfs" / f"{file_id}.pdf"
        if not pdf_path.exists():
            return {"status": "ok", "id": rec.id}
        try:
            rag._collection.delete(where={"file_id": file_id})
        except Exception:
            pass
        data = pdf_path.read_bytes()
        try:
            text = rag.parse_pdf(data)
        except Exception:
            return {"status": "ok", "id": rec.id}
        chunks = rag.chunk_text(text, chunk_size=320, overlap=40)
        rag.persist_chunks(file_id=file_id, session_id=rec.session_id, chunks=chunks)
        return {"status": "ok", "id": rec.id}
    else:
        # For image/audio originals we saved on disk; try to rebuild text
        if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
            # Remove existing vectors before re-adding
            try:
                rag._collection.delete(where={"file_id": file_id})
            except Exception:
                pass
            base = Path("data") / "uploads" / "images"
            path = None
            for ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
                p = base / f"{file_id}{ext}"
                if p.exists():
                    path = p
                    break
            if path and path.exists():
                from app.services.ocr import OcrService
                ocr = OcrService()
                text = ocr.extract_text(path.read_bytes())
                chunks = rag.chunk_text(text, chunk_size=320, overlap=40)
                rag.persist_chunks(file_id=file_id, session_id=rec.session_id, chunks=chunks, source_type="image")
        elif suffix in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
            try:
                rag._collection.delete(where={"file_id": file_id})
            except Exception:
                pass
            base = Path("data") / "uploads" / "audio"
            path = None
            for ext in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
                p = base / f"{file_id}{ext}"
                if p.exists():
                    path = p
                    break
            if path and path.exists():
                from app.services.transcription import AudioTranscriptionService
                transcriber = AudioTranscriptionService()
                segments = transcriber.transcribe(path.read_bytes())
                full_text = " ".join(s.get("text", "") for s in segments).strip()
                chunks = rag.chunk_text(full_text, chunk_size=320, overlap=40)
                metadatas = []
                start_time = float(segments[0]["start"]) if segments else 0.0
                end_time = float(segments[-1]["end"]) if segments else 0.0
                for i in range(len(chunks)):
                    metadatas.append(
                        {
                            "file_id": file_id,
                            "session_id": (rec.session_id if rec.session_id is not None else "GLOBAL"),
                            "chunk_index": i,
                            "source_type": "audio",
                            "start_time": start_time,
                            "end_time": end_time,
                        }
                    )
                rag.persist_documents(documents=chunks, metadatas=metadatas)
    return {"status": "ok", "id": rec.id}


@router.get("/files/{file_id}/download")
def download_original(file_id: str, db: Session = Depends(get_session)) -> FileResponse:
    rec = db.get(FileModel, file_id)
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    suffix = Path(rec.name).suffix.lower()
    if suffix == ".pdf":
        p = Path("data") / "uploads" / "pdfs" / f"{file_id}.pdf"
        if not p.exists():
            raise HTTPException(status_code=404, detail="Original not found")
        return FileResponse(str(p), media_type="application/pdf", filename=rec.name)
    if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
        base = Path("data") / "uploads" / "images"
        for ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
            p = base / f"{file_id}{ext}"
            if p.exists():
                mt = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".tiff": "image/tiff",
                    ".bmp": "image/bmp",
                    ".webp": "image/webp",
                }[ext]
                return FileResponse(str(p), media_type=mt, filename=rec.name)
        raise HTTPException(status_code=404, detail="Original not found")
    if suffix in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
        base = Path("data") / "uploads" / "audio"
        for ext in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
            p = base / f"{file_id}{ext}"
            if p.exists():
                mt = {
                    ".mp3": "audio/mpeg",
                    ".wav": "audio/wav",
                    ".m4a": "audio/mp4",
                    ".flac": "audio/flac",
                    ".ogg": "audio/ogg",
                }[ext]
                return FileResponse(str(p), media_type=mt, filename=rec.name)
        raise HTTPException(status_code=404, detail="Original not found")
    raise HTTPException(status_code=400, detail="Unsupported file type")


