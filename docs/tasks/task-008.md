# Task 008: Multi-source RAG Retrieval

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Source prioritization**: All sources treated equally; ranking purely by similarity score.
- ✅ **Context token budget**: 50k total (from Task 005), chunks selected based solely on highest similarity regardless of source type.
- ✅ **Session scope**: Retrieve from current session + global entries; no cross-session retrieval in MVP.
- ✅ **Source filtering**: Add `sources=["pdf","image","audio"]` parameter to `/api/chat`, defaulting to all.
- ✅ **Debug mode**: Show rankings separately per source type in debug output.

## Overview
This task upgrades the RAG retrieval system to work across multiple data sources (PDF, image OCR, audio transcription) in a single query.  
It unifies results from different sources into one ranking, while also allowing optional filtering by source type.

**Scope includes:**
- Query ChromaDB for all configured source types in parallel (PDF, image, audio).
- Merge results into a single ranking sorted by similarity score.
- Limit combined context to 50k tokens total.
- Allow API parameter to filter sources used in retrieval.
- Provide debug output that shows rankings separately per source type.

**Scope excludes:**
- Cross-session retrieval (future task).
- Custom weighting for sources (future task).

## Task Type
- [x] **Backend**
- [ ] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] `/api/chat` can retrieve context from PDFs, images, and audio at once.
- [x] Retrieval queries ChromaDB by `source_type` and merges results.
- [x] Results are ranked by similarity score, ignoring source type.
- [x] Context selection dynamically picks highest-ranked chunks up to 50k token limit.
- [x] API accepts `sources` parameter (list of strings), defaults to all sources.
- [x] Debug mode outputs separate rankings for each source type.

### Integration & Quality
- [x] Tests (TDD):
  - Retrieval returns mixed-source chunks ranked correctly.
  - Filtering by `sources` parameter works.
  - Debug output contains separate rankings.
  - Token budget is respected when mixing sources.
- [x] Configurable parameters in `config.py`:
  - Token budget (default 50k).
  - Default enabled sources.

## Backend Requirements
- [x] Reuse existing retrieval logic from PDF/image/audio RAG tasks.
- [x] Implement merging and sorting by similarity score.
- [x] Ensure `source_type` metadata is consistently applied across all entries.
- [x] Optimize for parallel querying of multiple source types.

## Expected Outcomes
- **For the user**: AI can answer questions using information from all available formats at once.
- **For the system**: Unified multi-source retrieval pipeline.
- **For developers**: Extensible system for adding more source types later.
- **For QA**: Ability to test retrieval from combined and filtered sources.

## Document References
- Related PRD sections: *Multi-source RAG*
- Related ADRs: **ADR-005 (RAG Architecture)**, **ADR-003 (Database Choice)**, **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 8 – Multi-source RAG*
- Dependencies: **Task 004**, **Task 005**, **Task 006**, **Task 007**

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Created: `tests/rag_multi/test_multi_source_retrieval.py`
- Modified: `app/api/chat.py`, `app/core/config.py`

**Key Technical Decisions**
- Unified retrieval within `chat` endpoint using existing `RagService`; no separate service module needed.
- Added `sources` array in request body; defaults to `pdf,image,audio` via `get_default_enabled_sources()`.
- Emitted `per_source` rankings in SSE debug payload alongside existing `citations`/`chunks` to avoid breaking prior behavior.
- Cache key includes `sources` to prevent stale mixed results.
- Token budget enforced with simple per-chunk estimate (≈500 tokens) consistent with prior tasks.

**API Endpoints**
- `/api/chat` — accepts optional `sources: ["pdf"|"image"|"audio"]` and emits `per_source` in debug output when enabled.

**Challenges & Solutions**
- Preserving existing SSE token stream and debug schema: kept prior fields and added `per_source` to extend non-invasively.
- Efficient retrieval across sources: executed session + global queries concurrently, then split/merge by `source_type` with unified ranking.
- Deterministic testing: used FAKE embeddings backend and isolated Chroma path per test.

**Notes for Future Tasks**
- Consider custom weighting per source and cross-session retrieval.
- Improve token counting with real tokenizer; surface citations with `source_type` in model output when model integration lands.
