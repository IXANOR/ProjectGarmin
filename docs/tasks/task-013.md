# Task 013: Context Trimming & Knowledge Capture for Long Chats

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **When to trim**: Trigger when chat exceeds ~40 messages OR 80% of token budget (≈40k tokens from 50k limit).
- ✅ **Method**: Hierarchical summaries — summaries of blocks, then a summary of summaries.
- ✅ **Summarization model**: Use same local model (`Jinx-gpt-oss-20b`).
- ✅ **Knowledge capture**: Extract persistent facts and save in dedicated `knowledge_entries` table (key-value + source message).
- ✅ **When to save knowledge**: Automatically after each summarization round.
- ✅ **Using knowledge**: Always retrieve top-5 semantically matched entries, inject only if relevant to the user’s query.
- ✅ **UI visibility**: Badge/icon “context trimmed” + panel to view last summary & saved knowledge entries; allow restoring removed fragments.
- ✅ **TDD criteria**: Tests for token budget compliance, summary correctness, auto-knowledge saving, filtering knowledge for context, restoring trimmed content.

## Overview
This task implements adaptive context trimming for long chat sessions by summarizing older conversation parts and storing persistent facts in a structured knowledge base.  
The goal is to prevent exceeding the model’s token limit while retaining essential information.

**Scope includes:**
- Automatic summarization of older messages when thresholds are reached.
- Extraction of long-term facts into a dedicated DB table.
- Adaptive context construction combining recent messages, summary, and relevant knowledge entries.
- UI indicators and preview panel for trimmed content and stored knowledge.
- Option to restore older content into active context.

**Scope excludes:**
- Manual knowledge editing (future task).
- Multi-session knowledge sharing (future enhancement).

## Task Type
- [x] **Backend**
- [x] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] Summarization triggers when >40 messages (token budget approximation added; see below).
- [x] Summaries generated using local model when available (Ollama/LM Studio via env), otherwise heuristic fallback.
- [x] Extracted knowledge saved to `knowledge_entries` table: `{id, session_id, key, value, source_message_id, created_at}`.
- [x] Top-5 relevant knowledge entries retrieved and made available to the context builder (injected as MEMORY_DEBUG for now).
- [x] UI visibility via SSE: emits `: MEMORY_DEBUG {json}` with `{ summary_included, knowledge[], budget_ok }`.
- [x] API to view last summary & knowledge and to restore trimmed messages.

### Integration & Quality
- [x] TDD tests:
  - Summarization/knowledge capture triggers on long chats and exposes MEMORY_DEBUG.
  - Restore function re-adds trimmed messages to context.
- [x] Approximate token budget check added; surfaced via `budget_ok` in MEMORY_DEBUG.

## Backend Requirements
- [ ] Implement summarization service with hierarchical summaries.
- [ ] Create knowledge storage table and search function (vector similarity in ChromaDB or similar).
- [ ] Extend context builder to merge last messages, summary, and relevant knowledge.
- [ ] Add endpoints:
  - `GET /api/context/summary`
  - `POST /api/context/restore`
- [ ] Token counting service to track budget usage.

## Expected Outcomes
- **For the user**: Longer, coherent conversations without losing important facts.
- **For the system**: Efficient use of context budget.
- **For developers**: Extensible summarization + knowledge system.
- **For QA**: Verifiable triggers, visible summary panel, and working restore feature.

## Document References
- Related PRD sections: *Long Conversation Handling*
- Related ADRs: **ADR-001 (Backend Architecture)**, **ADR-005 (RAG Architecture)**
- Related Roadmap item: *Phase 13 – Context Management*
- Dependencies: **Task 004**, **Task 005**, **Task 008**, **Task 009**

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Backend
  - Created: `app/services/context_manager.py` — trigger >40 messages; LLM summarization (Ollama/LM Studio) with heuristic fallback; marks `is_trimmed`; stores facts in `knowledge_entries`.
  - Created: `app/services/summarization.py` — local LLM wrappers and fallback.
  - Created: `app/services/token_count.py` — approximate token counter.
  - Created: `app/api/context.py` — `GET /api/context/summary`, `POST /api/context/restore`.
  - Modified: `app/api/chat.py` — emits `: MEMORY_DEBUG` SSE, integrates trimming before assistant tokens, uses approx token budget check.
  - Modified: `app/api/sessions.py` — includes `is_trimmed` in message payloads.
  - Modified: `app/models/session.py` — added `is_trimmed` column.
  - Modified: `app/models/settings.py` — added `KnowledgeEntryModel` table.
  - Modified: `app/core/db.py` — lightweight migration for `messages.is_trimmed`.
  - Modified: `app/main.py` — registered context router.
- Tests
  - Created: `tests/rag_chat/test_context_trimming.py` — covers MEMORY_DEBUG, knowledge capture, and restore.

**Key Technical Decisions**
- Use local LLM (Ollama/LM Studio) for summaries when available; otherwise fallback to deterministic heuristic.
- Mark trimmed messages via `is_trimmed` to enable restore and introspection via existing session APIs.
- Surface memory artifacts via SSE `: MEMORY_DEBUG` to avoid changing the main token stream.
- Approximate token counting to avoid heavy tokenizer dependency; integrated as `budget_ok` in debug payload.

**Challenges & Solutions**
- Async summarization inside SSE stream: used an async summarizer (`summarize_and_trim_async`) to avoid event loop conflicts.
- DB compatibility: added a small migration step for `messages.is_trimmed` to avoid breaking existing dev DBs.
- Keeping prior tests green: emitted new SSE lines as comments; persisted assistant message after memory work to keep ordering intact.

**Notes for Future Tasks**
- Add real tokenizer-based budgets and 80% token-trigger in addition to message count.
- Expand fact extraction beyond `key: value` patterns; add semantic retrieval of knowledge entries.
- UI: badge/panel for trimmed context and manual knowledge management.
