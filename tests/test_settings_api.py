import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_global_settings_get_defaults_and_update():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Defaults
        resp = await client.get("/api/settings/global")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {
            "temperature",
            "top_p",
            "max_tokens",
            "presence_penalty",
            "frequency_penalty",
        }
        assert data["temperature"] == 0.7
        assert data["top_p"] == 1.0
        assert data["max_tokens"] == 1024
        assert data["presence_penalty"] == 0.0
        assert data["frequency_penalty"] == 0.0

        # Update a couple of fields
        upd = await client.post(
            "/api/settings/global",
            json={"temperature": 0.3, "top_p": 0.8},
        )
        assert upd.status_code == 200
        body = upd.json()
        assert body["temperature"] == 0.3
        assert body["top_p"] == 0.8
        # Unchanged fields remain at defaults
        assert body["max_tokens"] == 1024
        assert body["presence_penalty"] == 0.0
        assert body["frequency_penalty"] == 0.0

        # Read back
        again = await client.get("/api/settings/global")
        assert again.status_code == 200
        data2 = again.json()
        assert data2["temperature"] == 0.3
        assert data2["top_p"] == 0.8


@pytest.mark.asyncio
async def test_session_settings_overrides_and_fallback_to_global():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a session
        create = await client.post("/api/sessions", json={"name": "S1"})
        assert create.status_code == 201
        session_id = create.json()["id"]

        # Ensure global is known
        await client.post(
            "/api/settings/global",
            json={"temperature": 0.5, "top_p": 0.9, "max_tokens": 2048},
        )

        # Initially, effective settings equal global; no overrides
        get0 = await client.get(f"/api/settings/session/{session_id}")
        assert get0.status_code == 200
        body0 = get0.json()
        assert set(body0.keys()) == {"session_id", "effective", "overrides"}
        assert body0["session_id"] == session_id
        eff0 = body0["effective"]
        assert eff0["temperature"] == 0.5
        assert eff0["top_p"] == 0.9
        assert eff0["max_tokens"] == 2048
        assert eff0["presence_penalty"] == 0.0
        assert eff0["frequency_penalty"] == 0.0
        assert body0["overrides"] == {}

        # Set a partial override for the session
        set_over = await client.post(
            f"/api/settings/session/{session_id}",
            json={"top_p": 0.7},
        )
        assert set_over.status_code == 200
        over = set_over.json()["overrides"]
        assert over == {"top_p": 0.7}

        # Now effective reflects override for top_p and global for the rest
        get1 = await client.get(f"/api/settings/session/{session_id}")
        assert get1.status_code == 200
        body1 = get1.json()
        eff1 = body1["effective"]
        assert eff1["temperature"] == 0.5  # from global
        assert eff1["top_p"] == 0.7        # overridden
        assert eff1["max_tokens"] == 2048  # from global
        assert eff1["presence_penalty"] == 0.0
        assert eff1["frequency_penalty"] == 0.0


