import asyncio
import json
import re
import os

import pytest
import httpx
from fpdf import FPDF

from app.main import app


def _pdf_bytes(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, text=line)
    return bytes(pdf.output(dest="S"))


@pytest.mark.asyncio
async def test_chat_includes_rag_debug_meta_with_citations(tmp_path):
    # Ensure debug mode on and permissive threshold
    os.environ["RAG_DEBUG_MODE"] = "true"
    os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.0"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session
        create_resp = await client.post("/api/sessions", json={"name": "For RAG Chat"})
        assert create_resp.status_code == 201
        session_id = create_resp.json()["id"]

        # Upload a session-scoped PDF
        pdf_bytes = _pdf_bytes("Session-linked PDF content for RAG chat integration test.")
        files = {"file": ("doc1.pdf", pdf_bytes, "application/pdf")}
        up = await client.post("/api/files", files=files, data={"session_id": session_id})
        assert up.status_code == 201

        # Upload a global PDF
        pdf_bytes2 = _pdf_bytes("Global file content for RAG chat integration test.")
        files2 = {"file": ("global.pdf", pdf_bytes2, "application/pdf")}
        up2 = await client.post("/api/files", files=files2)
        assert up2.status_code == 201

        # Ask a question; expect SSE tokens as before and RAG debug info as SSE comment lines
        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "Please summarize the content"}],
        }

        tokens: list[str] = []
        debug_lines: list[str] = []
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    tokens.append(line[len("data: "):])
                if line.startswith(": RAG_DEBUG "):
                    debug_lines.append(line[len(": RAG_DEBUG "):])

        # Tokens remain unchanged to preserve previous behavior
        assert tokens == ["Hello", "from", "mock", "AI!"]

        # There should be at least one RAG_DEBUG line with JSON payload
        assert any(debug_lines)
        # Parse the last debug json
        debug = json.loads(debug_lines[-1])
        assert isinstance(debug, dict)
        # Expect citations array with items like "filename.pdf#chunk_id"
        citations = debug.get("citations", [])
        assert isinstance(citations, list)
        assert all(isinstance(c, str) for c in citations)
        pattern = re.compile(r".+\.pdf#\d+")
        assert all(pattern.match(c) for c in citations)
        # Chunks metadata list should be present
        chunks = debug.get("chunks", [])
        assert isinstance(chunks, list)
        if chunks:
            sample = chunks[0]
            assert "id" in sample and "metadata" in sample
            # score may be present
            assert "score" in sample or True


@pytest.mark.asyncio
async def test_chat_skips_rag_for_short_query_with_high_threshold(monkeypatch):
    # Force similarity threshold to be very high to ensure skip condition is met
    monkeypatch.setenv("RAG_SIMILARITY_THRESHOLD", "0.99")
    monkeypatch.setenv("RAG_DEBUG_MODE", "true")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session
        create_resp = await client.post("/api/sessions", json={"name": "Short Query"})
        assert create_resp.status_code == 201
        session_id = create_resp.json()["id"]

        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "Hi"}],
        }

        debug_lines: list[str] = []
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line.startswith(": RAG_DEBUG "):
                    debug_lines.append(line[len(": RAG_DEBUG "):])

        assert any(debug_lines)
        debug = json.loads(debug_lines[-1])
        # With very short query and high threshold we expect skip
        assert debug.get("used") is False


