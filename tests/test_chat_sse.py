import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_chat_sse_streams_tokens_and_persists_in_db():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session first (Task 003 requires existing session_id)
        create_resp = await client.post("/api/sessions", json={"name": "Test Session"})
        assert create_resp.status_code == 201
        session = create_resp.json()
        session_id = session["id"]

        payload = {
            "session_id": session_id,
            "messages": [{"role": "user", "content": "Hello"}],
        }

        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            tokens: list[str] = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    tokens.append(line[len("data: "):])

        assert tokens == ["Hello", "from", "mock", "AI!"]

        # Verify persistence via GET /api/sessions/{id}
        get_resp = await client.get(f"/api/sessions/{session_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        messages = data.get("messages", [])
        assert len(messages) >= 2
        # Last two are user then assistant
        assert messages[-2]["role"] == "user"
        assert messages[-2]["content"] == "Hello"
        assert messages[-1]["role"] == "assistant"
        assert messages[-1]["content"] == "Hello from mock AI!"

