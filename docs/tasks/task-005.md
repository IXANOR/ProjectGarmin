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
- [ ] On receiving a chat request, retrieve relevant chunks from ChromaDB for given session_id + global scope.
- [ ] Dynamically choose the number of chunks to fit within 50k token limit.
- [ ] Include chosen chunks in the context section of the prompt, with metadata for source citations.
- [ ] Append citations in model answers in format `[filename.pdf#chunk_id]`.
- [ ] Skip retrieval when message <10 chars AND no match above 0.2 score.
- [ ] Cache retrieval results for 5 min.
- [ ] Timeout retrieval after 6 seconds and proceed without RAG context if exceeded.

### Integration & Quality
- [ ] End-to-end TDD:
  - Retrieval returns top matches within budget.
  - Short/no-match queries skip RAG.
  - Answers include citations when RAG is used.
  - Debug meta contains chunk IDs and scores.
- [ ] Configurable parameters for token budget, top-k, similarity threshold, cache TTL, and timeout.
- [ ] Proper error handling if ChromaDB is unavailable (fallback to no-RAG).

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
[To be filled after completion:]
- **Files Created/Modified**: `app/api/chat.py`, `app/services/rag.py`, `tests/rag_chat/`  
- **Key Technical Decisions**: dynamic chunk selection, large context budget usage, citation format.
- **API Endpoints**: Updated `/api/chat`.
- **Components Created**: Retrieval + prompt assembly logic.
- **Challenges & Solutions**: Managing large context without performance degradation.
- **Notes for Future Tasks**: Add reranking, add other RAG data sources, UI support for citations.
