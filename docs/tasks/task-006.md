# Task 006: RAG for Images (OCR + Embeddings)

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Supported formats**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
- ✅ **OCR Engine**: Tesseract OCR (offline, open-source, widely supported).
- ✅ **Embedding model**: Same as PDFs (`multi-qa-MiniLM-L12-v2`) for consistent vector space.
- ✅ **Store originals**: Yes, store in `/data/uploads/images/` for debugging and UI preview.
- ✅ **Metadata**: Add `source_type="image"` plus `file_id`, `session_id`, `chunk_index`.
- ✅ **API endpoints**: Separate `/api/images` with `POST`, `GET`, `DELETE`.
- ✅ **Chunking**: Same as PDFs — 500 tokens with 50-token overlap.

## Overview
This task extends the RAG pipeline to handle image files.  
Users can upload supported image formats, which will be processed via OCR, chunked, embedded, and stored in persistent ChromaDB.  
Files are linked to sessions but can also be global (no session_id).

**Scope includes:**
- OCR extraction from uploaded images.
- Text chunking (500 tokens, overlap 50) and embedding using the same model as PDFs.
- Persistent storage in ChromaDB with metadata identifying file type and source.
- Storing original images in `/data/uploads/images/`.
- Separate API endpoints for managing images (`/api/images`).
- Listing and deleting uploaded images.

**Scope excludes:**
- Image-to-text captioning (future task).
- Non-textual feature embeddings (e.g., CLIP) — future task.

## Task Type
- [x] **Backend**
- [ ] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [ ] `POST /api/images` accepts multipart upload:
  - `file`: supported image file.
  - `session_id` (optional).
  - Returns: file record with ID and metadata.
- [ ] OCR text extracted with Tesseract OCR.
- [ ] Chunking into 500-token segments with 50-token overlap.
- [ ] Embedding with `multi-qa-MiniLM-L12-v2` and storing in ChromaDB `/data/chroma`.
- [ ] Metadata includes `source_type="image"`.
- [ ] Store original image in `/data/uploads/images/`.
- [ ] `GET /api/images?session_id=...` lists images for session + global.
- [ ] `DELETE /api/images/{id}` removes metadata, vectors, and original file.

### Integration & Quality
- [ ] Tests (TDD):
  - OCR extraction returns expected text from sample image.
  - Chunking & embedding tested for shape and metadata.
  - API tests for upload, list, delete.
  - Validation for unsupported formats and size limits.
- [ ] Configurable parameters in `config.py`:
  - Supported formats.
  - OCR language(s) — default `eng`.
  - Max file size.
- [ ] `.gitignore` excludes `/data/uploads/images/**`.

## Backend Requirements
- [ ] Use `pytesseract` for OCR; ensure it works cross-platform (Windows 11 support).
- [ ] Integration with existing ChromaDB persistence.
- [ ] Reuse chunking/embedding services from PDFs to keep DRY.
- [ ] Ensure consistent metadata so `/api/chat` RAG retrieval works with PDFs and images seamlessly.

## Expected Outcomes
- **For the user**: Ability to upload images with text and have them included in AI's knowledge base.
- **For the system**: Unified RAG pipeline for both PDFs and images.
- **For developers**: Extensible architecture for adding more formats later.
- **For QA**: Verified OCR, embedding, and persistence with test assets.

## Document References
- Related PRD sections: *RAG for Images*
- Related ADRs: **ADR-005 (RAG Architecture)**, **ADR-003 (Database Choice)**, **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 6 – RAG for Images*
- Dependencies: **Task 004**, **Task 005**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `app/api/images.py`, `app/services/ocr.py`, `tests/rag_images/`
- **Key Technical Decisions**: Tesseract OCR, same embedding model as PDFs, storing originals.
- **API Endpoints**: `POST /api/images`, `GET /api/images`, `DELETE /api/images/{id}`
- **Components Created**: OCR service, image upload handler.
- **Challenges & Solutions**: Cross-platform OCR installation, large image handling.
- **Notes for Future Tasks**: Add CLIP embeddings, image captioning, multilingual OCR.
