import asyncio
import json
import os

import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_chat_appends_search_context_when_enabled(monkeypatch):
    # Enable search globally and debug logging
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Toggle search settings on
        upd = await client.post(
            "/api/settings/search",
            json={"allow_internet_search": True, "debug_logging": True},
        )
        assert upd.status_code == 200

        # Create a session
        create = await client.post("/api/sessions", json={"name": "Search Chat"})
        assert create.status_code == 201
        session_id = create.json()["id"]

        # Ask a query that should trigger a web search (heuristic: contains 'latest' keyword)
        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "What is the latest news about Python?"}],
        }

        debug_lines = []
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line.startswith(": SEARCH_DEBUG "):
                    debug_lines.append(line[len(": SEARCH_DEBUG "):])

        # Expect at least one SEARCH_DEBUG line in debug mode when search is enabled
        assert any(debug_lines)
        last = json.loads(debug_lines[-1])
        assert isinstance(last, dict)
        # It should include the query text and a results field (may be empty if offline)
        assert "query" in last
        assert "results" in last


