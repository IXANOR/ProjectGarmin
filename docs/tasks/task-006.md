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
- [x] `POST /api/images` accepts multipart upload:
  - `file`: supported image file.
  - `session_id` (optional).
  - Returns: file record with ID and metadata.
- [x] OCR text extracted with Tesseract OCR.
- [x] Chunking into 500-token segments with 50-token overlap.
- [x] Embedding with `multi-qa-MiniLM-L12-v2` and storing in ChromaDB `/data/chroma`.
- [x] Metadata includes `source_type="image"`.
- [x] Store original image in `/data/uploads/images/`.
- [x] `GET /api/images?session_id=...` lists images for session + global.
- [x] `DELETE /api/images/{id}` removes metadata, vectors, and original file.

### Integration & Quality
- [x] Tests (TDD):
  - OCR extraction returns expected text from sample image (monkeypatched to avoid system OCR dependency in CI).
  - Chunking & embedding tested for shape and metadata (includes `source_type`).
  - API tests for upload, list, delete.
  - Validation for unsupported formats and size limits.
- [x] Configurable parameters in `config.py`:
  - Supported formats via `SUPPORTED_IMAGE_FORMATS` (comma-separated, e.g. `.png,.jpg,.jpeg`).
  - OCR language(s) via `OCR_LANG` — default `eng`.
  - Max file size via `IMAGES_MAX_FILE_SIZE_MB` — default `10`.
- [x] `.gitignore` excludes `/data/uploads/images/**`.

## Backend Requirements
- [x] Use `pytesseract` for OCR; ensure it works cross-platform (Windows 11 support). Tests use monkeypatch; runtime uses Pillow+pytesseract.
- [x] Integration with existing ChromaDB persistence.
- [x] Reuse chunking/embedding services from PDFs to keep DRY.
- [x] Ensure consistent metadata so `/api/chat` RAG retrieval works with PDFs and images seamlessly.

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
- **Files Created/Modified**:
  - Created: `app/api/images.py`, `app/services/ocr.py`, `app/core/config.py`, `tests/rag_images/test_ocr_and_embedding.py`, `tests/test_images_api.py`
  - Modified: `app/services/rag.py` (added `source_type` metadata), `app/main.py` (router include), `.gitignore`, `pyproject.toml`
- **Key Technical Decisions**:
  - Reuse existing `RagService` for chunking/embeddings to keep DRY and ensure a unified vector space.
  - Add optional `source_type` metadata set to `image` for image-origin chunks.
  - Implement `OcrService` using Pillow + pytesseract with lazy import and test-friendly fallback; OCR language configurable via env.
  - Centralize image configs in `app/core/config.py` (supported formats, OCR language, max file size).
- **API Endpoints**:
  - `POST /api/images` — upload image, OCR, chunk, embed, persist; save original under `/data/uploads/images/`.
  - `GET /api/images` — list images (session + global).
  - `DELETE /api/images/{id}` — remove vectors, DB record, and original file.
- **Components Created**: OCR service, image upload/list/delete handlers, config helpers.
- **Challenges & Solutions**:
  - Avoiding hard dependency on system Tesseract in tests → monkeypatch `pytesseract.image_to_string` and lazy-import within `OcrService`.
  - Ensuring no regressions to PDF RAG or chat flows → full test suite passes.
  - Handling large files → configurable max size guard with clear 400 error.
- **Notes for Future Tasks**:
  - Consider CLIP or multimodal embeddings and image captioning for non-text images.
  - Add multilingual OCR support and per-request language override.
  - Extend `/api/chat` to surface citations with `source_type` to differentiate sources if needed.
