import uuid

from fpdf import FPDF

from app.services.rag import RagService, FakeEmbeddingModel


def _make_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, text=line)
    return bytes(pdf.output(dest="S"))


def test_embeddings_persisted_and_retrievable(tmp_path):
    # Prepare service with fake embedder for determinism
    rag = RagService(chroma_path=tmp_path / "chroma", embedder=FakeEmbeddingModel(embed_dim=4))

    file_id = uuid.uuid4().hex
    session_id = uuid.uuid4().hex
    text = "This is a simple PDF with repeated words for embedding test. " * 10
    pdf_bytes = _make_pdf(text)

    # Process PDF: parse -> chunk -> embed -> persist
    parsed = rag.parse_pdf(pdf_bytes)
    chunks = rag.chunk_text(parsed, chunk_size=30, overlap=5)
    rag.persist_chunks(file_id=file_id, session_id=session_id, chunks=chunks)

    # Now retrieve top-k for a simple query and ensure we get non-empty results with metadata
    results = rag.query("embedding test", top_k=3, where={"file_id": file_id})
    assert len(results) > 0
    # Each result: {"text":..., "metadata": {"file_id":..., "session_id":..., "chunk_index": int}}
    for r in results:
        assert r["metadata"]["file_id"] == file_id
        assert r["metadata"]["session_id"] == session_id
        assert isinstance(r["metadata"]["chunk_index"], int)


