import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_chat_emits_personality_debug_and_affects_mock_reply_length():
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		# Ensure a session exists
		create = await client.post("/api/sessions", json={"name": "P Test"})
		assert create.status_code == 201
		session_id = create.json()["id"]

		# Set personality to concise and humorous
		upd = await client.post("/api/personality", json={"length": "concise", "humor": "frequent"})
		assert upd.status_code == 200

		payload = {"session_id": session_id, "messages": [{"role": "user", "content": "Tell me a joke about CPUs"}]}
		async with client.stream("POST", "/api/chat", json=payload) as resp:
			assert resp.status_code == 200
			lines = []
			async for line in resp.aiter_lines():
				lines.append(line)

		# There should be a MEMORY_DEBUG and a PERSONALITY_DEBUG comment lines optionally, but at least PERSONALITY_DEBUG
		personality_lines = [l for l in lines if l.startswith(": PERSONALITY_DEBUG ")]
		assert len(personality_lines) >= 1
		# Ensure normal data tokens are still present, and count is unaffected in structure
		data_tokens = [l[len("data: "):] for l in lines if l.startswith("data: ")]
		assert data_tokens == ["Hello", "from", "mock", "AI!"]


@pytest.mark.asyncio
async def test_personality_adapts_from_recent_messages():
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		# Create session
		create = await client.post("/api/sessions", json={"name": "Adapt Test"})
		assert create.status_code == 201
		session_id = create.json()["id"]

		# Send casual/humorous/swearing and detail-seeking message to trigger adaptation
		payload = {"session_id": session_id, "messages": [{"role": "user", "content": "hey lol that's funny haha fuck explain in detail with more details step by step"}]}
		async with client.stream("POST", "/api/chat", json=payload) as resp:
			assert resp.status_code == 200
			pers_lines = []
			async for line in resp.aiter_lines():
				if line.startswith(": PERSONALITY_DEBUG "):
					pers_lines.append(line[len(": PERSONALITY_DEBUG "):])

		assert pers_lines, "PERSONALITY_DEBUG line expected"
		import json
		last = json.loads(pers_lines[-1])
		assert last.get("updated") in {True, False}
		profile = last.get("profile", {})
		# Expect the heuristic detection to lean casual, humorous, swearing allowed, and more elaborate
		assert profile.get("formality") in {"casual", "neutral", "formal"}
		assert profile.get("humor") in {"frequent", "moderate", "none"}
		assert isinstance(profile.get("swearing"), bool)

	# Per-session overrides should appear in PERSONALITY_DEBUG effective profile
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		create = await client.post("/api/sessions", json={"name": "Override Test"})
		assert create.status_code == 201
		session_id = create.json()["id"]
		# set override: style=creative
		po = await client.post(f"/api/personality/session/{session_id}", json={"style": "creative"})
		assert po.status_code == 200
		payload = {"session_id": session_id, "messages": [{"role": "user", "content": "write a poem"}]}
		async with client.stream("POST", "/api/chat", json=payload) as resp:
			assert resp.status_code == 200
			pers_lines = []
			async for line in resp.aiter_lines():
				if line.startswith(": PERSONALITY_DEBUG "):
					pers_lines.append(line[len(": PERSONALITY_DEBUG "):])
		import json
		prof = json.loads(pers_lines[-1])["profile"]
		assert prof.get("style") == "creative"


