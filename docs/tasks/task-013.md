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
- [ ] Summarization triggers when >40 messages OR token budget >80%.
- [ ] Hierarchical summaries generated using local model.
- [ ] Extracted knowledge saved to `knowledge_entries` table: `{id, session_id, key, value, source_message_id, created_at}`.
- [ ] Top-5 relevant knowledge entries retrieved using semantic search & injected into prompt if relevant.
- [ ] UI shows “context trimmed” badge + panel with last summary and knowledge entries.
- [ ] UI option to restore older trimmed messages into context.

### Integration & Quality
- [ ] TDD tests:
  - Token budget never exceeded.
  - Summaries update correctly after new trimming.
  - Knowledge entries auto-saved and searchable.
  - Only relevant entries injected into context.
  - Restore function re-adds messages to context.
- [ ] Performance tests to ensure summarization overhead is minimal.

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
[To be filled after completion:]
- **Files Created/Modified**: `app/services/context_manager.py`, `app/db/knowledge_entries.py`, `frontend/components/context_summary/`
- **Key Technical Decisions**: Adaptive triggers, hierarchical summaries, knowledge injection filter.
- **API Endpoints**: As listed above.
- **Components Created**: Summary badge, preview panel, restore button.
- **Challenges & Solutions**: Keeping summaries relevant, avoiding noise in knowledge base.
- **Notes for Future Tasks**: Add manual knowledge management UI.
