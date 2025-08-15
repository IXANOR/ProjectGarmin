# Task 007: RAG for Audio (Transcription + Embeddings)

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Supported formats**: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`.
- ✅ **Transcription engine**: Faster-Whisper (offline, efficient, supports multi-language).
- ✅ **Languages**: `pl` + `en` prioritized, multi-language support enabled.
- ✅ **Store originals**: Yes, in `/data/uploads/audio/` for debugging and UI playback.
- ✅ **Metadata**: `source_type="audio"`, `file_id`, `session_id`, `chunk_index`, plus `start_time` / `end_time` for each chunk.
- ✅ **API endpoints**: Separate `/api/audio` with `POST`, `GET`, `DELETE`.
- ✅ **Chunking**: 500 tokens with 50-token overlap (consistent with PDFs/images). Future: optional time-based chunking.

## Overview
This task extends the RAG pipeline to handle audio files.  
Users can upload supported audio formats, which will be transcribed, chunked, embedded, and stored in persistent ChromaDB.  
Files are linked to sessions but can also be global (no session_id).  
Each chunk will include timing information for potential UI playback of exact segments.

**Scope includes:**
- Transcription via Faster-Whisper (GPU-accelerated if available).
- Text chunking (500 tokens, overlap 50) and embedding using same model as PDFs/images.
- Persistent storage in ChromaDB with audio-specific metadata.
- Storing original audio files in `/data/uploads/audio/`.
- API endpoints for uploading, listing, deleting audio files.
- Metadata includes timing for UI playback.

**Scope excludes:**
- Speaker diarization (future task).
- Audio feature embeddings (future task).
- Automatic language detection tuning (beyond Whisper defaults).

## Task Type
- [x] **Backend**
- [ ] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] `POST /api/audio` accepts multipart upload:
  - `file`: supported audio file.
  - `session_id` (optional).
  - Returns: file record with ID and metadata.
- [x] Transcription with Faster-Whisper, outputting text + timing for each segment.
- [x] Chunking transcription into 500-token segments with 50-token overlap.
- [x] Embedding with `multi-qa-MiniLM-L12-v2` and storing in ChromaDB `/data/chroma`.
- [x] Metadata includes `source_type="audio"`, `start_time`, `end_time`.
- [x] Store original audio in `/data/uploads/audio/`.
- [x] `GET /api/audio?session_id=...` lists audio files for session + global.
- [x] `DELETE /api/audio/{id}` removes metadata, vectors, and original file.

### Integration & Quality
- [x] Tests (TDD):
  - Transcription returns expected text from sample audio (monkeypatched for determinism).
  - Chunking & embedding tested for shape, metadata, and timing fields.
  - API tests for upload, list, delete.
  - Validation for unsupported formats and file size.
- [x] Configurable parameters in `config.py`:
  - Supported formats.
  - Whisper model size (`base`, `small`, `medium`, `large-v2`).
  - Max file size.
- [x] `.gitignore` excludes `/data/uploads/audio/**`.

## Backend Requirements
- [x] Use `faster-whisper` for transcription with GPU if available.
- [x] Store timing for each chunk in ChromaDB metadata.
- [x] Reuse chunking/embedding services from PDFs/images to maintain consistency.
- [x] Ensure multi-language support with Whisper auto-detection.

## Expected Outcomes
- **For the user**: Ability to upload audio and have spoken content included in AI's knowledge base.
- **For the system**: Unified RAG pipeline for PDFs, images, and audio.
- **For developers**: Extensible pipeline for adding more audio features later.
- **For QA**: Verified transcription, chunking, embedding, and retrieval with test audio files.

## Document References
- Related PRD sections: *RAG for Audio*
- Related ADRs: **ADR-005 (RAG Architecture)**, **ADR-003 (Database Choice)**, **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 7 – RAG for Audio*
- Dependencies: **Task 004**, **Task 005**, **Task 006**

## Implementation Summary (Post-Completion)
- **Files Created/Modified**:
  - Created: `app/api/audio.py`, `app/services/transcription.py`, `tests/rag_audio/test_transcription_and_embedding.py`, `tests/test_audio_api.py`
  - Modified: `app/services/rag.py` (added `persist_documents` and stable ID generation), `app/core/config.py` (audio formats, size, model size), `app/main.py` (router include), `.gitignore` (audio uploads)
- **Key Technical Decisions**:
  - Use Faster-Whisper with lazy initialization and a safe fallback to enable testing without the binary.
  - Persist chunk metadata with `source_type="audio"`, `start_time`, `end_time`; initial timing uses overall bounds per file for simplicity.
  - Reuse existing `RagService` for chunking/embeddings to keep a unified vector space with PDFs/images.
  - Introduce `persist_documents` to allow custom per-chunk metadata (e.g., timings) and stable IDs based on `file_id:chunk_index`.
  - Config-driven audio formats and size limits; default `WHISPER_MODEL_SIZE=base`.
- **API Endpoints**:
  - `POST /api/audio` — upload audio, transcribe, chunk, embed, persist; save original under `/data/uploads/audio/`.
  - `GET /api/audio` — list audio files (session + global).
  - `DELETE /api/audio/{id}` — remove vectors, DB record, and original file.
- **Challenges & Solutions**:
  - Heavy ASR dependency: used lazy import and placeholder model class to allow monkeypatch-based tests.
  - Timing granularity: stored start/end per chunk now; precise per-chunk mapping can be added later without breaking schema.
  - Consistency with images/PDF flows: mirrored patterns for validation, persistence, and listing.
- **Notes for Future Tasks**:
  - Implement time-based chunking and precise segment-to-chunk timing alignment.
  - Add speaker diarization and per-request language override; expose Whisper model size override if needed.
  - Surface audio citations with timings in `/api/chat` responses.
