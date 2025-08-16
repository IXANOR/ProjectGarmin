import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_session_personality_overrides_merge_and_persist():
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		# Create a session
		create = await client.post("/api/sessions", json={"name": "P Sess"})
		assert create.status_code == 201
		session_id = create.json()["id"]

		# Read defaults for session
		resp = await client.get(f"/api/personality/session/{session_id}")
		assert resp.status_code == 200
		data = resp.json()
		assert data["session_id"] == session_id
		assert set(data.keys()) == {"session_id", "effective", "overrides"}
		assert isinstance(data["effective"], dict)
		assert isinstance(data["overrides"], dict)

		# Apply overrides
		upd = await client.post(f"/api/personality/session/{session_id}", json={"formality": "formal", "length": "concise"})
		assert upd.status_code == 200
		body = upd.json()
		assert body["session_id"] == session_id
		assert body["overrides"]["formality"] == "formal"
		assert body["overrides"]["length"] == "concise"

		# Read back and verify effective reflects overrides
		again = await client.get(f"/api/personality/session/{session_id}")
		assert again.status_code == 200
		merged = again.json()
		eff = merged["effective"]
		assert eff["formality"] == "formal"
		assert eff["length"] == "concise"


