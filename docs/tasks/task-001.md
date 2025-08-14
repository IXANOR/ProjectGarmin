# Task 001: Project repository initialization & development environment setup

## Questions for Stakeholder/Owner
- [x] **Python environment management**: Use Poetry (confirmed).
- [x] **Node.js version**: Set to 20.15.0 LTS.
- [x] **GitHub Actions**: Add from the start for CI with tests.
- [x] **Backend structure**: Modular (`app/api`, `app/models`, `app/services`, `app/core`).
- [x] **Frontend styling**: Use TailwindCSS from the start.

## Overview
This task sets up the foundation of the project repository, ensuring that both backend and frontend environments are ready for development using Test Driven Development (TDD). It will also establish a modular backend architecture, a styled frontend using TailwindCSS, and Continuous Integration (CI) via GitHub Actions to automatically run tests on each push.  
This is the first step in the roadmap and is critical for ensuring a consistent development environment and code quality from day one.

**Scope includes**:
- Repository initialization and `.gitignore` configuration.
- Poetry setup for backend dependency management.
- Node.js + Tauri + React + TailwindCSS setup for frontend.
- Basic FastAPI backend with modular structure.
- Dummy tests for both backend and frontend to verify TDD workflow.
- GitHub Actions workflow for automated test runs.

**Scope excludes**:
- Any AI model integration.
- Complex API endpoints beyond `/health`.

**Key challenge**:
Ensuring all tooling works smoothly across Windows 11, with TDD ready to go from the first commit.

## Task Type
- [x] **Setup/Infrastructure**
- [x] **Backend**
- [x] **Frontend**
- [x] **Documentation**

## Acceptance Criteria
### Core Functionality
- [x] `.gitignore` excludes:
  - Model weights
  - Cache files
  - Local DB
  - Frontend build artifacts
- [x] Backend scaffold with `/health` endpoint.
- [x] Frontend scaffold displaying placeholder chat UI.
- [x] Poetry environment configured with backend dependencies.
- [x] Node.js environment with Tauri + React + TailwindCSS configured.
- [x] Dummy test for backend `/health` endpoint passes.
- [x] Dummy test for frontend component passes.

### Integration & Quality
- [x] GitHub Actions workflow runs backend and frontend tests on push.
- [x] Code follows project conventions and structure.
- [x] Documentation updated with setup instructions.
- [x] Tests written before implementation (TDD).

## Backend Requirements
- [x] **Tests First**: Write failing test for `/health` endpoint.
- [x] **TDD Notes**: Initial test checks for 200 OK and JSON `{"status": "ok"}`.
- [x] **API Design**: `/health` GET endpoint returns status JSON.
- [x] **Data Validation**: Not applicable for this endpoint.
- [x] **Error Handling**: Endpoint always returns 200 unless server is down.
- [x] **Documentation**: Add endpoint description in API docs.

## Frontend Requirements
- [x] **Tests First**: Write failing test for rendering a placeholder chat component.
- [x] **TDD Notes**: Component renders “Chat placeholder” text on load.
- [x] **Component Design**: Minimal App component with placeholder chat box.
- [x] **UI/UX**: Not applicable yet for design polish.
- [x] **State Management**: Not applicable yet.
- [x] **API Integration**: Not applicable yet.
- [x] **Responsive**: Basic responsive layout with TailwindCSS classes.

## Expected Outcomes
- **For the user**: The application opens with a basic chat placeholder and backend responds to `/health`.
- **For the system**: Backend and frontend scaffolds are in place for future development.
- **For developers**: Fully working dev environment with TDD workflow and CI configured.
- **For QA**: Run `pytest` for backend, `vitest` for frontend; both pass initial dummy tests.

## Document References
- Related PRD sections: Non-Functional Scope, MVP
- Related ADRs: ADR-001, ADR-002, ADR-003, ADR-006
- Related Roadmap item: Phase 0 – Project Setup & Architecture Foundations
- Dependencies: None (first task)

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Backend
  - `pyproject.toml` — Poetry config with FastAPI, Uvicorn, pytest, httpx
  - `app/main.py` — FastAPI app with `/health` endpoint returning `{ "status": "ok" }`
  - `app/__init__.py`, `app/api/__init__.py`, `app/models/__init__.py`, `app/services/__init__.py`, `app/core/__init__.py` — modular package skeleton per ADR-001
  - `tests/test_health.py` — async API test using httpx ASGI transport
- Frontend
  - `frontend/package.json`, `frontend/tsconfig.json` — Vite + React + TypeScript + Vitest setup
  - `frontend/vite.config.ts`, `frontend/vitest.setup.ts` — Vitest jsdom env + jest-dom
  - `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css` — minimal app rendering “Chat placeholder”; Tailwind wired
  - `frontend/postcss.config.js`, `frontend/tailwind.config.ts` — TailwindCSS configuration
  - `frontend/src/App.test.tsx` — test asserting placeholder renders
- Tauri (per ADR-002)
  - `src-tauri/Cargo.toml`, `src-tauri/tauri.conf.json`, `src-tauri/src/main.rs` — minimal Tauri project config
- Tooling
  - `.github/workflows/ci.yml` — CI to run backend and frontend tests on push/PR
  - `.gitignore` — ignores model weights, caches, local DB, frontend and tauri build artifacts
  - `README.md` — setup instructions for backend/frontend and notes
  - `dev.ps1` — Windows PowerShell launcher that starts backend and frontend, auto-detects Node paths, and safely cleans `node_modules` on OneDrive

**Key Technical Decisions**
- Adopt FastAPI with an ASGI-compatible test client (`httpx.ASGITransport`) for fast unit tests.
- Use Vite + React + Tailwind + Vitest + RTL for the frontend test harness.
- Create a minimal Tauri crate alongside the frontend to align with ADR-002 without over-committing early.
- CI uses Python 3.11 and Node 20 per task, runs tests for both stacks.

**API Endpoints**
- `/health` — GET → `{"status": "ok"}`

**Components Created**
- `App` — minimal placeholder chat container (renders “Chat placeholder”).

**Challenges & Solutions**
- PowerShell chaining and missing tools locally: ran backend tests via a local venv and configured CI to validate both stacks on push.
- Frontend/Tauri setup without over-scoping: added minimal configs sufficient for tests and future growth.
- Windows specifics: paths with spaces and OneDrive file locks caused `npm` EPERM errors and Node PATH issues. Updated `dev.ps1` to use `Set-Location -LiteralPath`, prepend detected Node directories to PATH, alias `node.exe` if needed, and implement rename+`rmdir` fallback when deleting locked `node_modules`.

**Notes for Future Tasks**
- Consider adding `@tauri-apps/cli` as a dev dependency when packaging is needed.
- Decide whether to commit `poetry.lock` for reproducibility.
- Introduce integration/E2E tests (Playwright) as features land (see roadmap Phases 1–2).
- If EPERM issues persist with `node_modules` under OneDrive, consider moving the workspace outside OneDrive or configuring npm cache/workspace to a non-synced directory.
