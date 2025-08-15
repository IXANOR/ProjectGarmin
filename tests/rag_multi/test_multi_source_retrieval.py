import os
import uuid

import pytest
import httpx

from app.main import app
from app.services.rag import RagService


def _persist_sample_docs(session_id: str, chroma_path: str) -> None:
    # Ensure the service uses the same persistent path and FAKE embedder via env
    rag = RagService(chroma_path=chroma_path)

    # Create a few chunks per source type
    sources = {
        "pdf": ["pdf alpha information", "pdf beta details"],
        "image": ["image gamma content", "image delta description"],
        "audio": ["audio epsilon notes", "audio zeta transcript"],
    }

    for src_type, chunks in sources.items():
        file_id = uuid.uuid4().hex
        rag.persist_chunks(file_id=file_id, session_id=session_id, chunks=chunks, source_type=src_type)


@pytest.mark.asyncio
async def test_chat_multi_source_retrieval_combines_and_ranks(monkeypatch, tmp_path):
    # Isolate vector store and use fake embeddings for determinism and speed
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDINGS_BACKEND", "FAKE")
    monkeypatch.setenv("RAG_DEBUG_MODE", "true")
    monkeypatch.setenv("RAG_SIMILARITY_THRESHOLD", "0.0")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session
        create_resp = await client.post("/api/sessions", json={"name": "Multi-Source"})
        assert create_resp.status_code == 201
        session_id = create_resp.json()["id"]

        # Persist mixed-source documents directly via RAG
        _persist_sample_docs(session_id=session_id, chroma_path=str(tmp_path / "chroma"))

        # Ask a question without specifying sources (defaults to all)
        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "please summarize the data across files"}],
        }

        debug_lines: list[str] = []
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line.startswith(": RAG_DEBUG "):
                    debug_lines.append(line[len(": RAG_DEBUG "):])

        assert any(debug_lines)
        import json as _json

        debug = _json.loads(debug_lines[-1])
        assert debug.get("used") is True

        # Verify per-source rankings are present and contain at least two distinct sources
        per_source = debug.get("per_source", {})
        assert isinstance(per_source, dict)
        non_empty_sources = [k for k, v in per_source.items() if isinstance(v, list) and len(v) > 0]
        assert len(non_empty_sources) >= 2

        # Overall selected chunks should be sorted by score (non-increasing) when scores present
        selected = debug.get("chunks", [])
        assert isinstance(selected, list) and len(selected) > 0
        scores = [c.get("score") for c in selected]
        # Only compare adjacent pairs where both scores are not None
        for a, b in zip(scores, scores[1:]):
            if a is not None and b is not None:
                assert a >= b


@pytest.mark.asyncio
async def test_chat_sources_filter_limits_results_to_selected_types(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDINGS_BACKEND", "FAKE")
    monkeypatch.setenv("RAG_DEBUG_MODE", "true")
    monkeypatch.setenv("RAG_SIMILARITY_THRESHOLD", "0.0")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/api/sessions", json={"name": "Filter Sources"})
        assert create_resp.status_code == 201
        session_id = create_resp.json()["id"]

        _persist_sample_docs(session_id=session_id, chroma_path=str(tmp_path / "chroma"))

        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "give me context"}],
            "sources": ["image"],
        }

        debug_lines: list[str] = []
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line.startswith(": RAG_DEBUG "):
                    debug_lines.append(line[len(": RAG_DEBUG "):])

        assert any(debug_lines)
        import json as _json
        debug = _json.loads(debug_lines[-1])

        # All selected chunks must be from image source
        for c in debug.get("chunks", []):
            meta = c.get("metadata", {})
            assert meta.get("source_type") == "image"

        per_source = debug.get("per_source", {})
        # Only 'image' should have non-empty ranking when filtered
        assert "image" in per_source and isinstance(per_source["image"], list) and len(per_source["image"]) > 0
        other = {k: v for k, v in per_source.items() if k != "image"}
        assert all(len(v) == 0 for v in other.values())


@pytest.mark.asyncio
async def test_chat_token_budget_respected_with_mixed_sources(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDINGS_BACKEND", "FAKE")
    monkeypatch.setenv("RAG_DEBUG_MODE", "true")
    monkeypatch.setenv("RAG_SIMILARITY_THRESHOLD", "0.0")
    # 1000 token budget with ~500 tokens per chunk => max 2 chunks
    monkeypatch.setenv("RAG_TOKEN_BUDGET", "1000")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/api/sessions", json={"name": "Budget"})
        assert create_resp.status_code == 201
        session_id = create_resp.json()["id"]

        # Persist more than two chunks across sources
        _persist_sample_docs(session_id=session_id, chroma_path=str(tmp_path / "chroma"))

        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "summarize"}],
        }

        debug_lines: list[str] = []
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line.startswith(": RAG_DEBUG "):
                    debug_lines.append(line[len(": RAG_DEBUG "):])

        assert any(debug_lines)
        import json as _json
        debug = _json.loads(debug_lines[-1])

        selected = debug.get("chunks", [])
        assert len(selected) <= 2


