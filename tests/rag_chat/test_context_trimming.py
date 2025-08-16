import json
import os

import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_summarization_and_knowledge_capture_trigger_and_memory_debug(monkeypatch):
    # Keep generous budget but ensure debug enabled
    monkeypatch.setenv("RAG_DEBUG_MODE", "true")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session
        create = await client.post("/api/sessions", json={"name": "Long Chat"})
        assert create.status_code == 201
        session_id = create.json()["id"]

        # Build >40 user messages to trigger trimming; include some fact-like lines
        msgs = []
        msgs.append({"role": "user", "content": "Name: Alice"})
        msgs.append({"role": "user", "content": "Favorite color: blue"})
        msgs.append({"role": "user", "content": "City: Warsaw"})
        for i in range(38):
            msgs.append({"role": "user", "content": f"Filler message {i}"})

        payload = {"session_id": session_id, "messages": msgs}

        memory_debug_lines: list[str] = []
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line.startswith(": MEMORY_DEBUG "):
                    memory_debug_lines.append(line[len(": MEMORY_DEBUG "):])

        assert memory_debug_lines, "Expected MEMORY_DEBUG SSE line"
        md = json.loads(memory_debug_lines[-1])
        assert md.get("summary_included") is True
        know = md.get("knowledge", [])
        # Expect at least the captured fact to appear
        joined = "\n".join(know)
        assert "favorite color" in joined.lower()
        assert "blue" in joined.lower()
        assert md.get("budget_ok") is True

        # Context API should return last summary and saved knowledge entries
        summary_resp = await client.get(f"/api/context/summary", params={"session_id": session_id})
        assert summary_resp.status_code == 200
        body = summary_resp.json()
        assert body.get("summary") and isinstance(body["summary"], str)
        entries = body.get("knowledge", [])
        assert isinstance(entries, list) and len(entries) >= 1
        # Ensure the entry contains our key/value
        combined = " ".join([f"{e.get('key')}: {e.get('value')}" for e in entries])
        assert "favorite color" in combined.lower()
        assert "blue" in combined.lower()


@pytest.mark.asyncio
async def test_restore_trimmed_messages(monkeypatch):
    monkeypatch.setenv("RAG_DEBUG_MODE", "false")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session
        create = await client.post("/api/sessions", json={"name": "Restore Chat"})
        session_id = create.json()["id"]

        # Trigger trimming with >40 messages
        msgs = [{"role": "user", "content": f"Msg {i}: key{i}: value{i}"} for i in range(45)]
        payload = {"session_id": session_id, "messages": msgs}
        resp = await client.post("/api/chat", json=payload)
        assert resp.status_code == 200

        # Inspect messages; expect some trimmed
        detail = await client.get(f"/api/sessions/{session_id}")
        assert detail.status_code == 200
        messages = detail.json()["messages"]
        trimmed_count = sum(1 for m in messages if m.get("is_trimmed"))
        assert trimmed_count > 0

        # Restore a few trimmed messages
        restore = await client.post("/api/context/restore", json={"session_id": session_id, "count": 5})
        assert restore.status_code == 200
        restored = restore.json().get("restored", 0)
        assert restored == 5

        detail2 = await client.get(f"/api/sessions/{session_id}")
        messages2 = detail2.json()["messages"]
        trimmed_count2 = sum(1 for m in messages2 if m.get("is_trimmed"))
        assert trimmed_count2 == max(0, trimmed_count - 5)


