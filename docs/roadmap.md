# Project Roadmap – Local Personal AI Assistant (“Garmin”)

## Phase 0 – Project Setup & Architecture Foundations
**Goal:** Prepare repository, tooling, and architecture before writing main features.  
**Tasks:**
- Initialize Git repository.
- Configure `.gitignore`:
  - Ignore model weights, large cache files, local DB.
  - Ignore build artifacts from Tauri/Node.
- Set up `/docs` structure:
  - `/docs/ADR`
  - `/docs/architecture`
  - `/docs/notes`
- Prepare `README.md` with project description and basic run instructions.
- Set license file (MIT or Apache 2.0).
- Backend: create `pyproject.toml` or `requirements.txt`.
- Frontend: create `package.json`.
- Backend scaffold:
  - FastAPI basic app with `/health` endpoint.
- Frontend scaffold:
  - Tauri + React with basic chat UI placeholder.
- **TDD Setup:**
  - Backend: install and configure `pytest`, create `tests` folder, add first dummy test.
  - Frontend: install and configure `vitest` + `react-testing-library`, add first dummy test.

---

## Phase 1 – Backend MVP
**Goal:** Have a backend capable of handling AI chat requests locally.  
**Tasks (TDD-first):**
- Write failing API test for `/api/chat` returning model output.
- Implement Ollama integration for local model inference.
- Support streaming responses.
- Add session handling (in-memory).
- Write tests for session logic and error handling.

---

## Phase 2 – Frontend MVP
**Goal:** Display AI responses in the app.  
**Tasks (TDD-first):**
- Write failing test for rendering chat messages from API.
- Implement real-time message streaming from backend.
- UI: Chat area, input box, send button.
- Sidebar: Session list with basic navigation.
- Tests for message rendering, session switching.

---

## Phase 3 – Persistent Storage
**Goal:** Store sessions and user settings locally.  
**Tasks (TDD-first):**
- Write failing test for storing and retrieving messages in SQLite.
- Implement SQLModel integration.
- Add API for saving/loading sessions.
- Frontend: Add load and delete session UI.
- Tests for DB queries, data persistence.

---

## Phase 4 – RAG Integration (PDF MVP)
**Goal:** Allow AI to use uploaded PDFs as context.  
**Tasks (TDD-first):**
- Write failing API test for `/api/upload` (PDF).
- Implement ChromaDB integration.
- Parse and embed PDFs locally.
- Retrieve relevant chunks before model inference.
- Frontend: File upload UI and document list.
- Tests for PDF parsing, embedding, and retrieval.

---

## Phase 5 – Model Controls & Settings
**Goal:** Allow simple parameter tuning.  
**Tasks (TDD-first):**
- Write failing test for `/api/settings` endpoint.
- Backend: implement parameter storage and retrieval.
- Frontend: Settings UI with sliders/toggles for temperature, max tokens, reasoning mode.
- Tests for parameter persistence and validation.

---

## Phase 6 – Memory Optimization & Summarization
**Goal:** Handle long conversations efficiently.  
**References:** ADR-007 (Conversation Memory and Context Management)

**Tasks (TDD-first):**
- Add tests that after N messages a rolling `summary` artifact is created and older turns are compressed.
- Implement per-session memory artifacts in ChromaDB: `summary`, `facts`, `tools` (see ADR-007).
- Retrieve top 2–3 memory artifacts per turn under `RAG_PER_TURN_MEMORY_BUDGET_TOKENS` and inject into prompt.
- Tighten RAG defaults: `RAG_TOP_K_MAX=5`, `RAG_FINAL_TOP_K=3`, chunk 300/overlap 50.
- Optional: add re-ranking for top 20 and keep best 3.
- Add `: MEMORY_DEBUG` SSE lines to reveal what memory was injected.
- Tests for summarization triggers, memory retrieval under budget, and prompt token control.

---

## Phase 7 – Monitoring & Performance
**Goal:** Display system usage to the user.  
**Tasks (TDD-first):**
- Write failing test for `/api/system-stats`.
- Implement backend system metrics (CPU, GPU, RAM usage).
- Frontend: Display stats in top-right corner.
- Tests for correct metric display.

---

## Phase 8 – Optional Features & Polish
**Goal:** Improve UX and flexibility.  
**Tasks:**
- Per-session custom themes & fonts.
- Dark/light mode toggle.
- Plugin API skeleton.
- Web search plugin (if enabled).
- Small UI animations and polish.
- Write tests for UI theming and plugin loading.

---

## Phase 9 – Public Release
**Goal:** Make repo clean and ready for others.  
**Tasks:**
- Complete `README.md` with install & usage guide.
- Add screenshots/demo GIF.
- Provide `.env.example`.
- Review and finalize `/docs`.
- Ensure all tests pass before tagging release.
