# Task 010: RAG File Manager UI

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Panel structure**: One unified "Files" panel with three tabs (PDF, Images, Audio), with filtering by session.
- ✅ **Displayed data**: Filename, size, date uploaded, assigned session, number of chunks; for audio also transcription language.
- ✅ **Operations**: Upload (drag & drop + button), Delete (Soft + Hard), Download original, Reprocess (re-embedding), Reassign session (set global or change session).
- ✅ **Filters & sorting**: Filter by type (via tabs) and by session; sort by date/name.
- ✅ **Preview**:
  - PDF: metadata only.
  - Image: thumbnail, upload date, filename.
  - Audio: simple player, segment timings, metadata available after selecting file.
- ✅ **Search**: Search by filename only (full-text search deferred to future task).
- ✅ **Multi-upload**: Yes — queue with progress bar.
- ✅ **Delete types**:
  - Soft delete: file excluded from RAG context but still stored.
  - Hard delete: permanent removal from disk + ChromaDB.
- ✅ **Chat integration**: Clicking a file in manager sets RAG filter to “only this file” for active session.
- ✅ **TDD Frontend**: Test uploads, deletes, filters, previews, multi-upload queue, snapshot testing.

## Overview
This task creates a dedicated UI panel for managing all RAG files (PDF, images, audio).  
The panel enables filtering by session, file management actions, previews, and integration with the chat retrieval pipeline.

**Scope includes:**
- Unified "Files" UI with tabs for PDF, images, audio.
- Session-based filtering for all file types.
- Upload via drag & drop or file picker (multi-upload supported).
- File operations: Soft/Hard delete, reprocess, reassign session, download original.
- Preview features specific to file type.
- Integration with chat retrieval to filter RAG context by selected file.
- Persistent state reflecting backend changes.

**Scope excludes:**
- Full-text search in embeddings (future task).
- Batch reprocessing (future task).

## Task Type
- [x] **Frontend**
- [x] **Backend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [ ] Unified Files panel with three tabs: PDF, Images, Audio.
- [ ] File listing includes filename, size, date, session, chunk count, and transcription language for audio.
- [ ] Filters by session and type (tab selection).
- [ ] Upload supports multi-upload with queue and progress.
- [ ] Soft delete removes file from RAG context but keeps on disk.
- [ ] Hard delete removes file from disk and ChromaDB.
- [ ] Reprocess re-embeds file content in ChromaDB.
- [ ] Reassign session changes file ownership between sessions/global.
- [ ] Click on file sets active RAG filter to that file for current session.
- [ ] Preview features:
  - PDF: metadata.
  - Image: thumbnail, upload date, filename.
  - Audio: player + timing segments + metadata.

### Integration & Quality
- [ ] Backend endpoints for all file operations:
  - `GET /api/files?type=pdf|image|audio&session_id=...`
  - `POST /api/files/upload`
  - `DELETE /api/files/{id}?mode=soft|hard`
  - `POST /api/files/{id}/reprocess`
  - `POST /api/files/{id}/reassign`
- [ ] TDD tests:
  - Upload updates list immediately.
  - Delete soft/hard modes work.
  - Filtering by session updates list.
  - File previews render correctly.
  - Multi-upload queue processes all files.
  - Chat integration filter sets correctly.

## Backend Requirements
- [ ] Extend file service to handle soft/hard delete.
- [ ] Add endpoint for reassigning sessions.
- [ ] Implement queue processing for multi-upload.
- [ ] Ensure ChromaDB sync after soft/hard delete and reprocess.
- [ ] Return file previews (thumbnail, metadata) in list endpoint.

## Expected Outcomes
- **For the user**: Easy management of all uploaded RAG files from one place.
- **For the system**: Centralized file operations and consistent session filtering.
- **For developers**: Reusable backend endpoints for file management.
- **For QA**: Comprehensive frontend interaction tests.

## Document References
- Related PRD sections: *File Management UI*
- Related ADRs: **ADR-004 (Frontend Framework Choice)**, **ADR-005 (RAG Architecture)**
- Related Roadmap item: *Phase 10 – File Management UI*
- Dependencies: **Task 004**, **Task 005**, **Task 006**, **Task 007**, **Task 008**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `frontend/components/files/`, `app/api/files.py`
- **Key Technical Decisions**: Tabs per type, session filtering, click-to-filter chat integration.
- **API Endpoints**: As listed above.
- **Components Created**: Files panel, previews for PDF/image/audio.
- **Challenges & Solutions**: Sync between UI and backend, handling large multi-upload queues.
- **Notes for Future Tasks**: Add embedding full-text search, batch operations.
