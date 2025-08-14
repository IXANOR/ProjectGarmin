from fpdf import FPDF

from app.services.rag import RagService, FakeEmbeddingModel


def _make_pdf_with_tokens(num_tokens: int) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    tokens = ["tok"] * num_tokens
    line_width = 20
    for i in range(0, len(tokens), line_width):
        line = " ".join(tokens[i : i + line_width])
        pdf.multi_cell(pdf.epw, 10, text=line)
    return bytes(pdf.output(dest="S"))


def test_chunking_from_pdf_respects_size_and_overlap(tmp_path):
    # 1200 tokens -> with size=500, overlap=50, stride=450
    # expected chunks: ceil((1200-500)/450)+1 = 3
    pdf_bytes = _make_pdf_with_tokens(1200)
    rag = RagService(chroma_path=tmp_path / "chroma", embedder=FakeEmbeddingModel(embed_dim=8))

    text = rag.parse_pdf(pdf_bytes)
    chunks = rag.chunk_text(text, chunk_size=500, overlap=50)

    assert len(chunks) == 3

    # Verify overlap boundaries
    tokens0 = chunks[0].split()
    tokens1 = chunks[1].split()
    tokens2 = chunks[2].split()

    assert len(tokens0) <= 500
    assert len(tokens1) <= 500
    assert len(tokens2) <= 500

    assert tokens0[-50:] == tokens1[:50]
    assert tokens1[-50:] == tokens2[:50]


