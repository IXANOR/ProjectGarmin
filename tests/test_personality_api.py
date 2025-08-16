import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_personality_defaults_and_update_and_profiles():
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		# Defaults
		resp = await client.get("/api/personality")
		assert resp.status_code == 200
		data = resp.json()
		# required keys
		for key in ("formality", "humor", "swearing", "length", "detail", "proactivity", "style", "last_updated"):
			assert key in data
		# default shapes/types
		assert data["formality"] in {"formal", "neutral", "casual"}
		assert data["humor"] in {"none", "moderate", "frequent"}
		assert isinstance(data["swearing"], bool)
		assert data["length"] in {"concise", "normal", "elaborate"}
		assert data["detail"] in {"low", "medium", "high"}
		assert isinstance(data["proactivity"], bool)
		assert data["style"] in {"technical", "creative", "mixed"}

		# Partial update
		upd = await client.post("/api/personality", json={"formality": "casual", "humor": "moderate", "swearing": True})
		assert upd.status_code == 200
		body = upd.json()
		assert body["formality"] == "casual"
		assert body["humor"] == "moderate"
		assert body["swearing"] is True

		# PUT predefined profile
		prof = await client.put("/api/personality", json={"profile": "formal"})
		assert prof.status_code == 200
		after = prof.json()
		assert after["formality"] == "formal"
		assert after["humor"] == "none"
		assert after["swearing"] is False


