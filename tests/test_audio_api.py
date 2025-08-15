import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_audio_api_upload_list_delete_flow(monkeypatch):
	# Monkeypatch Faster-Whisper to avoid heavy dependency and make output deterministic
	from types import SimpleNamespace
	from app.services import transcription as tr_module

	def _fake_transcribe(self, audio_path_or_bytes, language=None):
		seg1 = SimpleNamespace(text="hello world", start=0.0, end=1.0)
		seg2 = SimpleNamespace(text="from audio", start=1.0, end=2.0)
		return [seg1, seg2], {"language": language or "en"}

	monkeypatch.setattr(tr_module.faster_whisper.WhisperModel, "transcribe", _fake_transcribe)

	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		# Create a session
		sess = await client.post("/api/sessions", json={"name": "For Audio"})
		assert sess.status_code == 201
		session_id = sess.json()["id"]

		# Upload valid audio for session
		files = {"file": ("voice.wav", b"FAKE_AUDIO", "audio/wav")}
		data = {"session_id": session_id}
		up = await client.post("/api/audio", files=files, data=data)
		assert up.status_code == 201
		rec = up.json()
		assert rec["name"] == "voice.wav"
		assert rec["session_id"] == session_id
		audio_id = rec["id"]

		# Upload global audio
		files2 = {"file": ("global.wav", b"FAKE_AUDIO2", "audio/wav")}
		up2 = await client.post("/api/audio", files=files2)
		assert up2.status_code == 201
		rec2 = up2.json()
		assert rec2["session_id"] is None

		# List by session should include both
		lst = await client.get(f"/api/audio", params={"session_id": session_id})
		assert lst.status_code == 200
		ids = {i["id"] for i in lst.json()}
		assert audio_id in ids and rec2["id"] in ids

		# Delete first audio
		delr = await client.delete(f"/api/audio/{audio_id}")
		assert delr.status_code == 204

		# Ensure it's gone
		lst2 = await client.get(f"/api/audio", params={"session_id": session_id})
		assert all(i["id"] != audio_id for i in lst2.json())


@pytest.mark.asyncio
async def test_audio_api_rejects_unsupported_format():
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		files = {"file": ("not-audio.txt", b"hello", "text/plain")}
		resp = await client.post("/api/audio", files=files)
		assert resp.status_code == 400
		assert "Unsupported" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_audio_api_rejects_too_large(monkeypatch):
	# Set a low max size
	monkeypatch.setenv("AUDIO_MAX_FILE_SIZE_MB", "0.0001")  # ~100 bytes
	transport = httpx.ASGITransport(app=app)
	async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
		data = b"A" * 200  # slightly larger than limit
		files = {"file": ("big.wav", data, "audio/wav")}
		resp = await client.post("/api/audio", files=files)
		assert resp.status_code == 400
		assert "large" in resp.json().get("detail", "").lower()


