import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_search_settings_defaults_and_update():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Defaults
        resp = await client.get("/api/settings/search")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"allow_internet_search", "debug_logging", "has_bing_api_key"}
        assert data["allow_internet_search"] is False
        assert data["debug_logging"] is False
        assert data["has_bing_api_key"] is False

        # Update values including providing a Bing API key
        upd = await client.post(
            "/api/settings/search",
            json={"allow_internet_search": True, "debug_logging": True, "bing_api_key": "test-key-123"},
        )
        assert upd.status_code == 200
        body = upd.json()
        assert body["allow_internet_search"] is True
        assert body["debug_logging"] is True
        assert body["has_bing_api_key"] is True

        # Read back
        again = await client.get("/api/settings/search")
        assert again.status_code == 200
        data2 = again.json()
        assert data2["allow_internet_search"] is True
        assert data2["debug_logging"] is True
        assert data2["has_bing_api_key"] is True


