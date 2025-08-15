import io
import uuid

import pytest
from PIL import Image, ImageDraw

from app.services.rag import RagService, FakeEmbeddingModel


def _png_bytes_with_text(text: str) -> bytes:
    img = Image.new("RGB", (300, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 40), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_ocr_chunk_and_persist_with_source_type_image(monkeypatch, tmp_path):
    # Prepare a fake OCR return to avoid requiring Tesseract binary
    from app.services import ocr as ocr_module

    monkeypatch.setattr(ocr_module.pytesseract, "image_to_string", lambda img, lang=None: "hello from image ocr")

    # Create sample image bytes
    img_bytes = _png_bytes_with_text("Hello")

    # Run OCR service
    service = ocr_module.OcrService()
    extracted = service.extract_text(img_bytes)
    assert "hello" in extracted.lower()

    # Chunk and persist into Chroma with source_type=image
    rag = RagService(chroma_path=tmp_path / "chroma", embedder=FakeEmbeddingModel(embed_dim=4))
    chunks = rag.chunk_text(extracted, chunk_size=10, overlap=2)
    file_id = uuid.uuid4().hex
    session_id = uuid.uuid4().hex
    rag.persist_chunks(file_id=file_id, session_id=session_id, chunks=chunks, source_type="image")

    results = rag.query("image ocr", top_k=3, where={"file_id": file_id})
    assert len(results) > 0
    assert all(r["metadata"]["file_id"] == file_id for r in results)
    assert all(r["metadata"]["session_id"] == session_id for r in results)
    # Ensure our new metadata is present
    assert all(r["metadata"].get("source_type") == "image" for r in results)


