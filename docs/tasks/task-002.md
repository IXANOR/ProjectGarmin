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
- [ ] Backend POST `/api/chat` accepts:
  ```json
  {
    "session_id": "abc123",
    "messages": [{ "role": "user", "content": "Hello" }]
  }
  ```
- [ ] Response is streamed via SSE, one token at a time from `"Hello from mock AI!"`.
- [ ] In-memory store keeps history for each session ID.
- [ ] Frontend sends request with `session_id` and message history.
- [ ] Frontend displays streamed tokens in the chat window.

### Integration & Quality
- [ ] Backend tests written first (TDD) and pass.
- [ ] Frontend tests for streaming message rendering written first and pass.
- [ ] Code is modular and matches project structure.
- [ ] SSE connection closes cleanly after sending response.

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
[To be filled after completion:]
- **Files Created/Modified**: List of actual files with brief purpose
- **Key Technical Decisions**: SSE implementation details, message format choices
- **API Endpoints**: `/api/chat`
- **Components Created**: Chat component SSE handler
- **Challenges & Solutions**: Any SSE or state management issues resolved
- **Notes for Future Tasks**: Any improvements for when real AI model is integrated
