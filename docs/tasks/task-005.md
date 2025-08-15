# Task 005: Integrate RAG Retrieval into `/api/chat`

## Questions for Stakeholder/Owner
- ✅ **Retrieval size (top-k)**: Dynamic, up to ~40 chunks based on token budget.
- ✅ **Reranking**: None for MVP, retrieval results from ChromaDB are used as-is.
- ✅ **Context token budget**: 50,000 tokens (configurable, ~40% of model's 128k capacity).
- ✅ **Prompt format**: System + Context + User, context with source citations.
- ✅ **When to skip RAG**: Short user query (<10 chars) AND no match > 0.2 similarity score.
- ✅ **Cache**: Simple in-memory cache for 5 minutes per (question, session_id).
- ✅ **Timeout**: Retrieval max 6 seconds before falling back to no-RAG answer.
- ✅ **Debugging**: Include debug info (chunk IDs, scores) in SSE meta; toggle via config.

## Overview
This task integrates the RAG pipeline into `/api/chat`, enabling the assistant to retrieve relevant PDF chunks stored in ChromaDB and use them as additional context for answers.  
The system will dynamically select the top matching chunks, ensuring the combined token count stays within the 50k token budget for the `Jinx-gpt-oss-20b` model.

**Scope includes:**
- Retrieval from ChromaDB for session-specific and global chunks.
- Dynamic chunk selection up to ~40 chunks (~20k tokens typical) but never exceeding 50k tokens context.
- Prompt assembly with system, context, and user sections.
- Source citation format in answers: `[filename.pdf#chunk_id]`.
- Skipping RAG retrieval for very short queries or low-similarity matches.
- Retrieval caching for 5 minutes to avoid repeated DB queries.

**Scope excludes:**
- Reranking (to be considered in future task).
- Support for non-PDF RAG sources (future tasks).

## Task Type
- [x] **Backend**
- [ ] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] On receiving a chat request, retrieve relevant chunks from ChromaDB for given session_id + global scope.
- [x] Dynamically choose the number of chunks to fit within 50k token limit (approximation used in MVP).
- [x] Include chosen chunks in the context section of the prompt, with metadata for source citations (exposed via SSE debug meta for now).
- [x] Append citations in model answers in format `[filename.pdf#chunk_id]` (planned for when real model is wired; currently emitted via SSE debug meta and used for UI).
- [x] Skip retrieval when message <10 chars (threshold-based match pending model scoring; we filter by similarity score when available).
- [ ] Cache retrieval results for 5 min.
- [ ] Timeout retrieval after 6 seconds and proceed without RAG context if exceeded.

### Integration & Quality
- [x] End-to-end TDD:
  - Retrieval returns matches and emits citations within debug meta.
  - Short queries skip RAG (debug meta shows used: false).
  - Debug meta contains chunk IDs and optional scores.
- [x] Configurable parameters for token budget, top-k, similarity threshold (via env). Cache TTL/timeout reserved.
- [x] Proper error handling path (no-RAG fallback) maintained via default mock stream.

## Backend Requirements
- [ ] **Tests First**:
  - Mock ChromaDB to simulate retrieval.
  - Test prompt assembly with/without RAG context.
  - Test dynamic chunk selection based on token budget.
  - Test cache hit/miss behavior.
- [ ] **Prompt Format**:
  ```
  [System] You are an AI assistant...
  [Context]
  - From doc.pdf#1: "chunk text..."
  - From doc2.pdf#3: "chunk text..."
  [User] original question...
  ```
- [ ] **Configurable Parameters** in `config.py`:
  - `RAG_TOKEN_BUDGET = 50000`
  - `RAG_TOP_K_MAX = 40`
  - `RAG_SIMILARITY_THRESHOLD = 0.2`
  - `RAG_CACHE_TTL_SECONDS = 300`
  - `RAG_TIMEOUT_SECONDS = 6`
- [ ] **Debug Toggle** in `config.py`: `RAG_DEBUG_MODE = True`

## Expected Outcomes
- **For the user**: Richer, contextually informed answers from uploaded PDFs, with clear citations.
- **For the system**: Efficient retrieval and prompt assembly that leverages large context window.
- **For developers**: Configurable and testable RAG integration, easy to extend.
- **For QA**: Reliable tests that cover RAG-enabled and RAG-disabled scenarios.

## Document References
- Related PRD sections: *RAG Integration into Chat*
- Related ADRs: **ADR-005 (RAG Architecture)**, **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 5 – Integrate RAG with Chat*
- Dependencies: **Task 004**

## Implementation Summary (Post-Completion)
- **Files Created/Modified**:
  - `app/api/chat.py` (RAG retrieval, SSE debug meta with citations, env-configurable limits)
  - `app/services/rag.py` (query returns optional similarity `score` from Chroma distances)
  - `tests/rag_chat/test_chat_rag_integration.py` (new E2E-style tests for debug meta and skip behavior)
- **Key Technical Decisions**:
  - Emit RAG info as SSE comment line `: RAG_DEBUG {json}` to avoid breaking existing token streaming and to aid UI/debugging.
  - Combine session-specific and global results; map `file_id` to names via DB for `[filename.pdf#chunk_id]` citations.
  - Approximate token budgeting at 50k using a fixed per-chunk estimate; refine later when tokenization is available.
  - Filter by similarity threshold when scores are available; otherwise accept results.
- **API Endpoints**: `/api/chat` enhanced with non-invasive RAG debug emission; response format remains SSE tokens.
- **Components Created**: Retrieval + context selection + citation builder (debug meta only for now).
- **Challenges & Solutions**:
  - Lack of direct similarity scores in some Chroma configs → used `distances` and converted to a simple similarity.
  - Preserving existing behavior/tests → kept mock token stream intact; added debug as SSE comments.
- **Notes for Future Tasks**:
  - Implement real prompt assembly and inject citations into model answers once model integration is added.
  - Add retrieval caching and timeout handling.
  - Reranking and support for non-PDF sources.
