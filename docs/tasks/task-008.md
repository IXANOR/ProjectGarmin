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
- [ ] `/api/chat` can retrieve context from PDFs, images, and audio at once.
- [ ] Retrieval queries ChromaDB by `source_type` and merges results.
- [ ] Results are ranked by similarity score, ignoring source type.
- [ ] Context selection dynamically picks highest-ranked chunks up to 50k token limit.
- [ ] API accepts `sources` parameter (list of strings), defaults to all sources.
- [ ] Debug mode outputs separate rankings for each source type.

### Integration & Quality
- [ ] Tests (TDD):
  - Retrieval returns mixed-source chunks ranked correctly.
  - Filtering by `sources` parameter works.
  - Debug output contains separate rankings.
  - Token budget is respected when mixing sources.
- [ ] Configurable parameters in `config.py`:
  - Token budget (default 50k).
  - Default enabled sources.

## Backend Requirements
- [ ] Reuse existing retrieval logic from PDF/image/audio RAG tasks.
- [ ] Implement merging and sorting by similarity score.
- [ ] Ensure `source_type` metadata is consistently applied across all entries.
- [ ] Optimize for parallel querying of multiple source types.

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
[To be filled after completion:]
- **Files Created/Modified**: `app/services/rag_multi.py`, `app/api/chat.py`, `tests/rag_multi/`
- **Key Technical Decisions**: Equal treatment of sources, optional filtering, debug separation of rankings.
- **API Endpoints**: Updated `/api/chat` to handle `sources` parameter.
- **Components Created**: Multi-source retrieval service.
- **Challenges & Solutions**: Efficient merging of large result sets, token budget management.
- **Notes for Future Tasks**: Add cross-session retrieval, custom weighting of sources.
