# Task 004: RAG – PDF MVP (persistent ChromaDB, embeddings, session-aware file management)

## Questions for Stakeholder/Owner
- [x] **Embedding model**: Use `sentence-transformers/multi-qa-MiniLM-L12-v2` (better accuracy, still lightweight).
- [x] **Vector store**: Use **ChromaDB** in persistent mode at `/data/chroma` (not in-memory).
- [x] **Chunking**: Fixed-size chunks (e.g., 500 tokens) with 50-token overlap for MVP.
- [x] **API surface**: Implement `POST /api/files`, `GET /api/files`, `DELETE /api/files/{id}` now.
- [x] **Scope & visibility**: Files linked to a `session_id` but also support global files (session_id=NULL). Retrieval will use session-specific + global files.

## Overview
This task implements the first Retrieval-Augmented Generation (RAG) capability for PDFs. Users can upload PDFs that will be parsed, chunked, embedded with the chosen embedding model, and stored in a persistent ChromaDB index on disk.  
The API also provides listing and deletion of uploaded files. For future chat augmentation, retrieval will pull both session-linked chunks and global chunks.  
The work is done **TDD-first** with unit/integration tests for parsing, embedding, persistence, and API behavior.

**Scope includes:**
- PDF upload and processing pipeline (parse → chunk → embed → persist to ChromaDB).
- Persistent ChromaDB at `/data/chroma` (auto-create if missing).
- API endpoints to manage files (create/list/delete).
- Storing file metadata in SQLite (file name, session_id, size, created_at).
- Tests for each step of the pipeline and API endpoints.

**Scope excludes:**
- Actual use of RAG results in `/api/chat` responses (to be wired in a later task).
- Non-PDF formats (images/audio) — future tasks.

**Key challenge:**
Ensuring consistent, deterministic chunking and robust PDF parsing (fallbacks for problematic PDFs), while keeping the embedding pipeline fast on Windows 11 with CPU-first embeddings.

## Task Type
- [x] **Backend**
- [x] **Integration**
- [ ] **Frontend** (basic upload UI in a later task)

## Acceptance Criteria
### Core Functionality
- [ ] `POST /api/files` accepts multipart upload with fields:
  - `file`: PDF file
  - `session_id` (optional): if omitted → global file
  - Returns: file record with ID and metadata
- [ ] The uploaded PDF is parsed, chunked (fixed 500 tokens, overlap 50), embedded with `multi-qa-MiniLM-L12-v2`, and stored in ChromaDB persistent index `/data/chroma` with metadata `{ file_id, session_id, chunk_index }`.
- [ ] `GET /api/files?session_id=...` lists files for the session **and** global files; without query param returns all (for admin/debug).
- [ ] `DELETE /api/files/{id}` removes the file record and its vectors from ChromaDB.
- [ ] SQLite table `files` created with columns: `id`, `name`, `session_id` (nullable), `size_bytes`, `created_at`.

### Integration & Quality
- [ ] Tests (pytest) written first: upload → parse → chunk → embed → persist; get list; delete.
- [ ] Proper input validation and 400 errors for non-PDF uploads.
- [ ] Clean architecture: `app/services/rag.py` (pipeline), `app/api/files.py` (endpoints), `app/models/file.py`.
- [ ] `.gitignore` includes `/data/chroma/**` (kept locally, not committed).

## Backend Requirements
- [ ] **Tests First**
  - **Parsing/chunking tests**: given a small sample PDF, chunks count and overlap rules are correct.
  - **Embedding tests**: embedding array shape conforms; mock/model fixture to avoid slow network during CI.
  - **Persistence tests**: vectors written to persistent Chroma; metadata stored in SQLite and correlates with vectors.
  - **API tests**: `POST /api/files`, `GET /api/files`, `DELETE /api/files/{id}` with success and error cases.
- [ ] **TDD Notes**
  - Use fixtures for temp directories; override Chroma path to a temp folder in tests.
  - For embeddings, prefer a switchable backend (real model locally, fallback mock for CI to avoid downloads).
- [ ] **API Design**
  - `POST /api/files` (multipart/form-data): returns `{ id, name, session_id, size_bytes, created_at }` (201)
  - `GET /api/files?session_id=...`: returns array of file records (200)
  - `DELETE /api/files/{id}`: returns 204
- [ ] **Data Validation**
  - Reject non-PDF MIME types; enforce max size (configurable) with clear error messages.
- [ ] **Error Handling**
  - Return 400 on invalid input; 404 on deleting/getting unknown file id.
- [ ] **Documentation**
  - Document endpoints, request/response formats, and how chunking/embedding works (short summary).

## Frontend Requirements (deferred)
- [ ] In a subsequent task: file upload UI, file list per session, delete control; wire `session_id` from current chat.

## Expected Outcomes
- **For the user**: Ability to upload PDFs that become part of the assistant’s knowledge base (persisted across restarts).
- **For the system**: A reliable RAG foundation (persistent embeddings, session-aware metadata).
- **For developers**: Clear pipeline and tests to safely extend with other formats (images/audio).
- **For QA**: Deterministic tests that validate chunking, embeddings, and persistence.

## Document References
- Related PRD sections: *RAG (Retrieval-Augmented Generation)*
- Related ADRs: **ADR-005 (RAG Architecture)**, **ADR-003 (Database Choice)**, **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 4 – RAG Integration (PDF MVP)*
- Dependencies: **Task 001**, **Task 002**, **Task 003**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `app/models/file.py`, `app/api/files.py`, `app/services/rag.py`, tests under `tests/rag/`  
- **Key Technical Decisions**: tokenization method for chunking, embedding batch size, Chroma collection naming
- **API Endpoints**: `POST /api/files`, `GET /api/files`, `DELETE /api/files/{id}`
- **Components Created**: N/A (backend only in this task)
- **Challenges & Solutions**: e.g., handling malformed PDFs or large files
- **Notes for Future Tasks**: wire retrieval into `/api/chat`; add image/audio support; add per-session settings in metadata
