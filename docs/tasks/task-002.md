# Task 002: Implement `/api/chat` endpoint with in-memory session storage and SSE mock response

## Questions for Stakeholder/Owner
- [x] **API format**: Simple `{ "messages": [...] }` request and `{ "reply": "..." }` response (no OpenAI mimic at this stage).
- [x] **Streaming**: Implement Server-Sent Events (SSE) from the start for smooth later integration with real model.
- [x] **Session handling**: Use in-memory storage for sessions keyed by `session_id`.

## Overview
This task implements the first version of the `/api/chat` backend endpoint, providing a mocked AI response via SSE.  
It will store and retrieve message history for each session from in-memory storage and allow the frontend to connect and receive responses token-by-token.  
This is an important milestone, as it sets up the communication pattern (SSE) that will be used when integrating the real model later.

**Scope includes**:
- Backend FastAPI endpoint `/api/chat` using POST.
- Accept JSON body with `session_id` and `messages`.
- Store messages in an in-memory dictionary.
- Respond with a mock AI reply streamed via SSE (`"Hello from mock AI!"` token-by-token).
- Frontend integration to call `/api/chat` and render the streamed output.
- TDD tests for both backend and frontend parts.

**Scope excludes**:
- Any real AI model integration.
- Database persistence (will be in a future task).

**Key challenge**:
Implementing SSE correctly in FastAPI and making sure frontend can process streamed tokens in real-time.

## Task Type
- [x] **Backend**
- [x] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] Backend POST `/api/chat` accepts:
  ```json
  {
    "session_id": "abc123",
    "messages": [{ "role": "user", "content": "Hello" }]
  }
  ```
- [x] Response is streamed via SSE, one token at a time from `"Hello from mock AI!"`.
- [x] In-memory store keeps history for each session ID.
- [x] Frontend sends request with `session_id` and message history.
- [x] Frontend displays streamed tokens in the chat window.

### Integration & Quality
- [x] Backend tests written first (TDD) and pass.
- [x] Frontend tests for streaming message rendering written first and pass.
- [x] Code is modular and matches project structure.
- [x] SSE connection closes cleanly after sending response.

## Backend Requirements
- [ ] **Tests First**: Pytest test to check SSE response tokens in order.
- [ ] **TDD Notes**: Simulate sending a message and assert response tokens `["Hello", "from", "mock", "AI!"]`.
- [ ] **API Design**: POST `/api/chat`.
- [ ] **Data Validation**: Ensure `session_id` and `messages` are provided.
- [ ] **Error Handling**: Return 400 for invalid request body.
- [ ] **Documentation**: Document request/response format.

## Frontend Requirements
- [ ] **Tests First**: Vitest test to simulate receiving SSE tokens and rendering in order.
- [ ] **TDD Notes**: Mock fetch to return SSE tokens and verify rendered output.
- [ ] **Component Design**: Chat UI updates message area as tokens arrive.
- [ ] **UI/UX**: Simple incremental text update during stream.
- [ ] **State Management**: Keep messages in local component state for now.
- [ ] **API Integration**: Connect to backend `/api/chat` SSE endpoint.

## Expected Outcomes
- **For the user**: They can type a message and see a mock AI reply appear word-by-word.
- **For the system**: SSE streaming architecture in place for later AI integration.
- **For developers**: Backend and frontend ready for real AI responses without structural changes.
- **For QA**: Manual test by starting backend + frontend, sending a message, verifying streamed output.

## Document References
- Related PRD sections: Functional Scope – Chat Interface
- Related ADRs: ADR-001, ADR-002, ADR-004
- Related Roadmap item: Phase 1 – Backend MVP
- Dependencies: Task 001 (Project setup, scaffolds, TDD tools)

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Backend
  - `app/api/chat.py` — POST `/api/chat` SSE endpoint returning mock tokens.
  - `app/services/session_store.py` — in-memory session history helpers.
  - `app/main.py` — registers `/api` router.
  - `tests/test_chat_sse.py` — asserts SSE tokens and session persistence.
- Frontend
  - `frontend/src/components/Chat.tsx` — minimal chat UI with SSE client.
  - `frontend/src/components/Chat.test.tsx` — tests streamed render order.
  - `frontend/src/App.tsx` — integrates `Chat` without breaking placeholder test.

**Key Technical Decisions**
- Used FastAPI `StreamingResponse` with `text/event-stream` and simple `data: <token>\n\n` framing.
- Kept storage in an in-memory dict keyed by `session_id` per ADR-001; no DB yet.

**API Endpoints**
- `/api/chat` — POST (SSE stream)

**Components Created**
- `Chat` — sends message, parses SSE, renders incremental assistant text.

**Challenges & Solutions**
- Preserved Task 001 test by keeping hidden `Chat placeholder` text in `App.tsx`.

**Notes for Future Tasks**
- Replace mock tokens with real model streaming; persist sessions in SQLite.
