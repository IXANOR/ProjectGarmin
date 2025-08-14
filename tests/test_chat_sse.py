import pytest
import httpx

from app.main import app
from app.services.session_store import get_history, clear_history


@pytest.mark.asyncio
async def test_chat_sse_streams_tokens_and_stores_history():
    session_id = "abc123"
    clear_history(session_id)

    payload = {
        "session_id": session_id,
        "messages": [{"role": "user", "content": "Hello"}],
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream("POST", "/api/chat", json=payload) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            tokens: list[str] = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    tokens.append(line[len("data: "):])

    assert tokens == ["Hello", "from", "mock", "AI!"]

    history = get_history(session_id)
    assert len(history) >= 1
    assert history[-1]["role"] == "user"
    assert history[-1]["content"] == "Hello"


