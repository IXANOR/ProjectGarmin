import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_create_list_get_delete_session_and_cascade_messages():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Initially empty
        resp = await client.get("/api/sessions")
        assert resp.status_code == 200
        assert resp.json() == []

        # Create
        create = await client.post("/api/sessions", json={"name": "My Session", "metadata": {"foo": "bar"}})
        assert create.status_code == 201
        session = create.json()
        assert "id" in session and session["name"] == "My Session"
        session_id = session["id"]

        # List
        resp = await client.get("/api/sessions")
        assert resp.status_code == 200
        sessions = resp.json()
        assert any(s["id"] == session_id for s in sessions)

        # Get details (no messages yet)
        detail = await client.get(f"/api/sessions/{session_id}")
        assert detail.status_code == 200
        body = detail.json()
        assert body["session"]["id"] == session_id
        assert body.get("messages") == []

        # Send chat; should persist user + assistant
        chat = await client.post("/api/chat", json={
            "session_id": session_id,
            "messages": [{"role": "user", "content": "Hi there"}],
        })
        assert chat.status_code == 200

        detail2 = await client.get(f"/api/sessions/{session_id}")
        assert detail2.status_code == 200
        messages = detail2.json()["messages"]
        assert [m["role"] for m in messages[-2:]] == ["user", "assistant"]
        assert messages[-1]["content"] == "Hello from mock AI!"

        # Delete and verify cascade
        delete = await client.delete(f"/api/sessions/{session_id}")
        assert delete.status_code == 204

        not_found = await client.get(f"/api/sessions/{session_id}")
        assert not_found.status_code == 404


@pytest.mark.asyncio
async def test_chat_unknown_session_returns_404():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/chat", json={
            "session_id": "does-not-exist",
            "messages": [{"role": "user", "content": "Hello"}],
        })
        assert resp.status_code == 404


