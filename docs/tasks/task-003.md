# Task 003: Persist chat sessions and messages in SQLite (with session metadata) and CRUD endpoints

## Questions for Stakeholder/Owner
- [x] **ORM**: Use **SQLModel** (per ADR-003) for simplicity and native Pydantic models; full SQLAlchemy would add boilerplate without clear benefit at this stage.
- [x] **Schema**: Add `metadata` JSON column on `sessions` for future per-session settings.
- [x] **API surface**: Implement CRUD endpoints now: list/get/create/delete sessions; `/api/chat` should persist messages.
- [x] **DB location**: Store database at `/data/app.db` (ensure folder exists and is gitignored).

## Overview
This task moves session and message storage from in-memory structures to a persistent **SQLite** database.  
It introduces a minimal relational schema (`sessions`, `messages`) with a `metadata` JSON column on sessions for future configuration overrides.  
We also expose REST endpoints for session CRUD and wire **`/api/chat`** to save incoming/outgoing messages under the correct `session_id`.  
All work is performed **TDD-first** with unit/integration tests.

**Scope includes:**
- Define SQLModel models for `Session` and `Message` with relationships.
- SQLite engine & session factory; create tables on startup.
- Persist messages from `/api/chat` (mock SSE) into DB.
- Endpoints: `POST /api/sessions`, `GET /api/sessions`, `GET /api/sessions/{id}`, `DELETE /api/sessions/{id}`.
- Basic validation and error handling (404 for unknown session).
- Tests for models and endpoints.

**Scope excludes:**
- Migrations tooling (Alembic) — optional future task.
- Advanced pagination/search — will come later.

**Key challenge:**
Designing clean model relationships and ensuring SSE chat flow persists user and assistant messages correctly without blocking the stream.

## Task Type
- [x] **Backend**
- [x] **Integration**
- [ ] **Frontend** (only minimal changes if needed to call new endpoints later)

## Acceptance Criteria
### Core Functionality
- [ ] DB file created at `/data/app.db` (auto-created if missing).
- [ ] `POST /api/sessions` creates a session (optional `name`, optional `metadata` JSON).
- [ ] `GET /api/sessions` returns all sessions (id, name, created_at).
- [ ] `GET /api/sessions/{id}` returns session details and ordered messages.
- [ ] `DELETE /api/sessions/{id}` removes session and its messages (cascade).
- [ ] `POST /api/chat` persists the incoming **user** message and the **assistant** reply (mock), associated to `session_id`.
- [ ] Unknown `session_id` returns 404.

### Integration & Quality
- [ ] Tests (pytest) written first: models, CRUD endpoints, chat persistence.
- [ ] Proper input validation and 400 responses on invalid payloads.
- [ ] Clean architecture: `app/models`, `app/api`, `app/services`, `app/core/db.py` for engine/session.
- [ ] `.gitignore` updated to ignore `/data/*.db*` and `/data/*.sqlite*`.

## Backend Requirements
- [ ] **Tests First**  
  - **Model tests**: creating Session and Message, relationship, cascade delete.  
  - **API tests**:  
    - Create/list/get/delete session flows (including 404 on unknown id).  
    - `/api/chat` persists both user and assistant messages in order for a given `session_id`.  
- [ ] **TDD Notes**  
  - Use `pytest` with temporary DB for tests (override DB URL to `sqlite://` in-memory or tmp file).  
  - Use FastAPI `TestClient` or `httpx.AsyncClient` to call endpoints.  
- [ ] **API Design**  
  - `POST /api/sessions` body: `{ "name": "optional", "metadata": { ... } }` → 201 with `{ "id": "...", "name": "...", "created_at": "...", "metadata": {...} }`  
  - `GET /api/sessions` → 200 list  
  - `GET /api/sessions/{id}` → 200 with `{ session, messages: [...] }`  
  - `DELETE /api/sessions/{id}` → 204  
  - `POST /api/chat` body: `{ "session_id": "uuid-or-string", "messages": [ { "role": "user", "content": "..." } ] }` → SSE mock reply  
- [ ] **Data Validation**  
  - `session_id` is required for `/api/chat`; messages must be non-empty list of `{role, content}`.  
- [ ] **Error Handling**  
  - 404 if session not found.  
  - 400 on invalid payloads.  
- [ ] **Documentation**  
  - Update API docs/comments for new endpoints and request/response formats.

## Frontend Requirements (if applicable now)
- [ ] None strictly required in this task. In a later task, add UI for listing/creating/deleting sessions and wiring `session_id` into chat requests.

## Expected Outcomes
- **For the user**: Chat history survives restarts; sessions can be created and managed later via UI.  
- **For the system**: A persistent storage layer enabling future features (search, RAG, memory).  
- **For developers**: Clear models and APIs; tests safeguarding future refactors.  
- **For QA**: Verify by running backend, creating a session, sending a chat message, and observing records in DB (or via GET endpoints).

## Document References
- Related PRD sections: *Functional Scope – Chat Interface; Persistent Storage; Long-Term Memory*  
- Related ADRs: **ADR-003 (Database Choice)**, **ADR-001 (Backend Architecture)**  
- Related Roadmap item: *Phase 3 – Persistent Storage*  
- Dependencies: **Task 001**, **Task 002**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `app/core/db.py`, `app/models/session.py`, `app/models/message.py`, `app/api/sessions.py`, changes to `app/api/chat.py`, tests under `tests/`  
- **Key Technical Decisions**: JSON type handling for `metadata`, cascade deletion, DB URL overrides in tests  
- **API Endpoints**: `POST/GET/GET/DELETE /api/sessions`, `POST /api/chat` (persistence)  
- **Components Created**: N/A (backend only)  
- **Challenges & Solutions**: e.g., ensuring SSE flow flushes while persisting messages  
- **Notes for Future Tasks**: Add pagination, search, and Alembic migrations
