import io
from typing import List

import pytest
import httpx
from PIL import Image, ImageDraw

from app.main import app
from app.services.rag import RagService


def _pdf_bytes(text: str) -> bytes:
    try:
        from fpdf import FPDF
    except Exception:  # pragma: no cover
        pytest.skip("fpdf not available")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, text=line)
    return bytes(pdf.output(dest="S"))


def _png_bytes(text: str) -> bytes:
    img = Image.new("RGB", (200, 80), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 30), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_unified_upload_and_list_with_type_and_chunk_count(monkeypatch, tmp_path):
    # Isolate vector store and make OCR/ASR deterministic
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDINGS_BACKEND", "FAKE")

    # OCR stub
    from app.services import ocr as ocr_module
    monkeypatch.setattr(ocr_module.pytesseract, "image_to_string", lambda img, lang=None: "image text here")

    # ASR stub
    from types import SimpleNamespace
    from app.services import transcription as tr_module

    def _fake_transcribe(self, audio_path_or_bytes, language=None):
        seg1 = SimpleNamespace(text="hello world", start=0.0, end=1.0)
        seg2 = SimpleNamespace(text="from audio", start=1.0, end=2.0)
        return [seg1, seg2], {"language": language or "en"}

    monkeypatch.setattr(tr_module.faster_whisper.WhisperModel, "transcribe", _fake_transcribe)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session used for all uploads
        sess = await client.post("/api/sessions", json={"name": "Files Manager"})
        assert sess.status_code == 201
        session_id = sess.json()["id"]

        # Multi-upload: pdf + image + audio
        files = [
            ("files", ("doc1.pdf", _pdf_bytes("pdf content for chunks"), "application/pdf")),
            ("files", ("pic.png", _png_bytes("hello"), "image/png")),
            ("files", ("clip.wav", b"FAKE_AUDIO", "audio/wav")),
        ]
        up = await client.post("/api/files/upload", files=files, data={"session_id": session_id})
        assert up.status_code == 201
        created: List[dict] = up.json()
        assert isinstance(created, list) and len(created) == 3
        ids_by_name = {c["name"]: c["id"] for c in created}

        # List by type: pdf
        lst_pdf = await client.get("/api/files", params={"type": "pdf", "session_id": session_id})
        assert lst_pdf.status_code == 200
        items_pdf = lst_pdf.json()
        assert len(items_pdf) == 1
        assert items_pdf[0]["name"].endswith(".pdf")
        assert items_pdf[0].get("chunk_count", 0) > 0

        # List by type: audio should contain transcription_language field (may be None/unknown)
        lst_audio = await client.get("/api/files", params={"type": "audio", "session_id": session_id})
        assert lst_audio.status_code == 200
        items_audio = lst_audio.json()
        assert len(items_audio) == 1
        assert "transcription_language" in items_audio[0]

        # List all types should be >= 3
        lst_all = await client.get("/api/files", params={"session_id": session_id})
        assert lst_all.status_code == 200
        assert len(lst_all.json()) >= 3


@pytest.mark.asyncio
async def test_soft_and_hard_delete_modes(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDINGS_BACKEND", "FAKE")

    from app.services import ocr as ocr_module
    monkeypatch.setattr(ocr_module.pytesseract, "image_to_string", lambda img, lang=None: "image text here")

    from types import SimpleNamespace
    from app.services import transcription as tr_module

    def _fake_transcribe(self, audio_path_or_bytes, language=None):
        seg1 = SimpleNamespace(text="hello world", start=0.0, end=1.0)
        return [seg1], {"language": language or "en"}

    monkeypatch.setattr(tr_module.faster_whisper.WhisperModel, "transcribe", _fake_transcribe)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        sess = await client.post("/api/sessions", json={"name": "Delete Modes"})
        session_id = sess.json()["id"]

        files = [
            ("files", ("doc2.pdf", _pdf_bytes("pdf"), "application/pdf")),
            ("files", ("clip2.wav", b"FAKE_AUDIO", "audio/wav")),
        ]
        up = await client.post("/api/files/upload", files=files, data={"session_id": session_id})
        created = up.json()
        pdf_id = next(c["id"] for c in created if c["name"].endswith(".pdf"))
        audio_id = next(c["id"] for c in created if c["name"].endswith(".wav"))

        # Soft delete PDF: it should disappear from list, but vectors remain
        soft = await client.delete(f"/api/files/{pdf_id}", params={"mode": "soft"})
        assert soft.status_code == 204
        lst_pdf = await client.get("/api/files", params={"type": "pdf", "session_id": session_id})
        assert all(it["id"] != pdf_id for it in lst_pdf.json())

        # Hard delete audio: removed from list and vectors deleted
        hard = await client.delete(f"/api/files/{audio_id}", params={"mode": "hard"})
        assert hard.status_code == 204

        # Verify vectors removed for audio
        rag = RagService(chroma_path=tmp_path / "chroma")
        got = rag._collection.get(where={"file_id": audio_id})
        ids0 = got.get("ids", [])
        # chroma returns nested lists sometimes
        if isinstance(ids0, list) and ids0 and isinstance(ids0[0], list):
            ids0 = ids0[0]
        assert len(ids0) == 0


@pytest.mark.asyncio
async def test_reassign_and_reprocess(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDINGS_BACKEND", "FAKE")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Two sessions
        s1 = (await client.post("/api/sessions", json={"name": "S1"})).json()["id"]
        s2 = (await client.post("/api/sessions", json={"name": "S2"})).json()["id"]

        up = await client.post(
            "/api/files/upload",
            files=[("files", ("swap.pdf", _pdf_bytes("content"), "application/pdf"))],
            data={"session_id": s1},
        )
        file_id = up.json()[0]["id"]

        # Reassign to session 2
        ra = await client.post(f"/api/files/{file_id}/reassign", json={"session_id": s2})
        assert ra.status_code == 200

        lst_s2 = await client.get("/api/files", params={"type": "pdf", "session_id": s2})
        ids_s2 = {i["id"] for i in lst_s2.json()}
        assert file_id in ids_s2

        # Verify vector metadata updated
        rag = RagService(chroma_path=tmp_path / "chroma")
        got = rag._collection.get(where={"file_id": file_id}, include=["metadatas"])  # type: ignore[arg-type]
        metas = got.get("metadatas", [])
        if isinstance(metas, list) and metas and isinstance(metas[0], list):
            metas = metas[0]
        assert metas and all(m.get("session_id") == s2 for m in metas)

        # Reprocess should succeed (idempotent) and keep chunks present
        rp = await client.post(f"/api/files/{file_id}/reprocess")
        assert rp.status_code == 200
        got2 = rag._collection.get(where={"file_id": file_id})
        ids0 = got2.get("ids", [])
        if isinstance(ids0, list) and ids0 and isinstance(ids0[0], list):
            ids0 = ids0[0]
        assert len(ids0) > 0


