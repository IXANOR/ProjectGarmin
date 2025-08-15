import uuid

import pytest

from app.services.rag import RagService, FakeEmbeddingModel


@pytest.mark.asyncio
async def test_transcription_chunk_and_persist_with_timings(monkeypatch, tmp_path):
	# Monkeypatch Faster-Whisper to avoid heavy dependency and make output deterministic
	from types import SimpleNamespace
	from app.services import transcription as tr_module

	def _fake_transcribe(self, audio_path_or_bytes, language=None):
		seg1 = SimpleNamespace(text="hello world", start=0.0, end=1.5)
		seg2 = SimpleNamespace(text="this is a test", start=1.6, end=3.2)
		return [seg1, seg2], {"language": language or "en"}

	monkeypatch.setattr(tr_module.faster_whisper.WhisperModel, "transcribe", _fake_transcribe)

	# Use the transcription service to obtain segments
	service = tr_module.AudioTranscriptionService()
	segments = service.transcribe(b"FAKE_AUDIO_BYTES", language="en")
	assert isinstance(segments, list) and len(segments) == 2
	assert segments[0]["text"].strip() != ""

	# Chunk the combined transcript text
	full_text = " ".join(s["text"] for s in segments)
	rag = RagService(chroma_path=tmp_path / "chroma", embedder=FakeEmbeddingModel(embed_dim=4))
	chunks = rag.chunk_text(full_text, chunk_size=10, overlap=2)
	assert len(chunks) >= 1

	# For simplicity in this unit test, map each chunk to the overall audio timing bounds
	start_time = segments[0]["start"]
	end_time = segments[-1]["end"]

	file_id = uuid.uuid4().hex
	session_id = uuid.uuid4().hex
	metadatas = []
	for i in range(len(chunks)):
		metadatas.append(
			{
				"file_id": file_id,
				"session_id": session_id,
				"chunk_index": i,
				"source_type": "audio",
				"start_time": float(start_time),
				"end_time": float(end_time),
			}
		)

	# Persist with custom metadata containing timings
	rag.persist_documents(documents=chunks, metadatas=metadatas)

	# Query back to verify metadata presence and correctness shape
	results = rag.query("hello test", top_k=3, where={"file_id": file_id})
	assert len(results) > 0
	for r in results:
		m = r["metadata"]
		assert m["file_id"] == file_id
		assert m["session_id"] == session_id
		assert isinstance(m["chunk_index"], int)
		assert m.get("source_type") == "audio"
		assert isinstance(m.get("start_time"), float)
		assert isinstance(m.get("end_time"), float)


