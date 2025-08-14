# Task 017: Conversation Logging & History Analysis

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Logging scope**: Messages from user and AI, timestamps, model parameters used, model response time, and RAG usage details.
- ✅ **Storage format**: Primary storage in DB for efficient querying + optional export to JSON/CSV via UI.
- ✅ **UI access**: Dedicated "Conversation History" tab with filters by session, date, and keyword search.
- ✅ **AI access**: AI can search its full history with the user for context recall.
- ✅ **Privacy controls**: User can delete individual messages or entire sessions, and toggle logging on/off.
- ✅ **Data retention**: No automatic limit, logs persist until manually deleted.
- ✅ **TDD coverage**: Tests for adding, filtering, exporting, deleting, and AI read-access to logs.

## Overview
This task implements a robust conversation logging system with integrated history analysis capabilities.  
Logs will be accessible to both the user (via UI) and AI (via backend API) for improved continuity and context recall.

**Scope includes:**
- Backend logic for storing, querying, and deleting logs.
- UI for viewing and filtering logs by session/date/keyword.
- Export feature for JSON/CSV formats.
- AI read-access to historical logs for better responses.
- Privacy features for selective deletion.

**Scope excludes:**
- Automated summarization of logs (handled in Task 013).

## Task Type
- [x] **Backend**
- [x] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [ ] Log each message with:
  - User or AI role
  - Timestamp
  - Model parameters used
  - Model response time
  - RAG usage details (if any)
- [ ] Store logs in DB with indexes for filtering/search.
- [ ] UI "Conversation History" tab with:
  - Session filter
  - Date filter
  - Keyword search
- [ ] Export to JSON and CSV from UI.
- [ ] AI API endpoint to retrieve conversation history context.
- [ ] User can delete individual messages or whole sessions.
- [ ] Logging can be toggled on/off in settings.

### Integration & Quality
- [ ] TDD tests:
  - Logging new messages.
  - Filtering by date/session/keyword.
  - Export to JSON/CSV.
  - Deletion of messages/sessions.
  - AI retrieval of historical messages.
- [ ] Verify performance with large datasets.

## Backend Requirements
- [ ] DB table `conversation_logs` with columns:
  `{id, session_id, role, content, timestamp, model_params, response_time, rag_usage}`.
- [ ] API endpoints:
  - `GET /api/logs`
  - `GET /api/logs/export`
  - `DELETE /api/logs/{id}`
  - `DELETE /api/logs/session/{id}`
  - `GET /api/logs/ai-context`
- [ ] Services for filtering, search, export, and deletion.

## UI Requirements
- [ ] "Conversation History" tab.
- [ ] Filters for session/date/keyword.
- [ ] Export buttons for JSON and CSV.
- [ ] Delete buttons for single message and session.
- [ ] Logging toggle in settings.

## Expected Outcomes
- **For the user**: Easy access to past conversations with powerful filtering and export tools.
- **For the AI**: Improved contextual awareness via history search.
- **For the system**: Efficient log storage with scalable querying.
- **For QA**: Clear test cases for logging, filtering, and exporting.

## Document References
- Related PRD sections: *Conversation History & AI Memory*
- Related ADRs: **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 17 – Logging & History*
- Dependencies: **Task 001**, **Task 013**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `services/log_service.py`, `frontend/components/history_tab/`
- **Key Technical Decisions**: DB storage with optional export formats.
- **API Endpoints**: Listed above.
- **Components Created**: History tab, export feature.
- **Challenges & Solutions**: Ensuring performance on large datasets.
- **Notes for Future Tasks**: Possible integration with summarization for compact history view.
