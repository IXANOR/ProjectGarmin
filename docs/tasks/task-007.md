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
- [ ] `POST /api/audio` accepts multipart upload:
  - `file`: supported audio file.
  - `session_id` (optional).
  - Returns: file record with ID and metadata.
- [ ] Transcription with Faster-Whisper, outputting text + timing for each segment.
- [ ] Chunking transcription into 500-token segments with 50-token overlap.
- [ ] Embedding with `multi-qa-MiniLM-L12-v2` and storing in ChromaDB `/data/chroma`.
- [ ] Metadata includes `source_type="audio"`, `start_time`, `end_time`.
- [ ] Store original audio in `/data/uploads/audio/`.
- [ ] `GET /api/audio?session_id=...` lists audio files for session + global.
- [ ] `DELETE /api/audio/{id}` removes metadata, vectors, and original file.

### Integration & Quality
- [ ] Tests (TDD):
  - Transcription returns expected text from sample audio.
  - Chunking & embedding tested for shape, metadata, and timing.
  - API tests for upload, list, delete.
  - Validation for unsupported formats and file size.
- [ ] Configurable parameters in `config.py`:
  - Supported formats.
  - Whisper model size (`base`, `small`, `medium`, `large-v2`).
  - Max file size.
- [ ] `.gitignore` excludes `/data/uploads/audio/**`.

## Backend Requirements
- [ ] Use `faster-whisper` for transcription with GPU if available.
- [ ] Store timing for each chunk in ChromaDB metadata.
- [ ] Reuse chunking/embedding services from PDFs/images to maintain consistency.
- [ ] Ensure multi-language support with Whisper auto-detection.

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
[To be filled after completion:]
- **Files Created/Modified**: `app/api/audio.py`, `app/services/transcription.py`, `tests/rag_audio/`
- **Key Technical Decisions**: Faster-Whisper, store timings, same embedding model as PDFs/images.
- **API Endpoints**: `POST /api/audio`, `GET /api/audio`, `DELETE /api/audio/{id}`
- **Components Created**: Transcription service, audio upload handler.
- **Challenges & Solutions**: Large audio files, multi-language handling, GPU acceleration.
- **Notes for Future Tasks**: Add diarization, CLIP embeddings, multilingual UI playback.
