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
- [ ] `.gitignore` excludes:
  - Model weights
  - Cache files
  - Local DB
  - Frontend build artifacts
- [ ] Backend scaffold with `/health` endpoint.
- [ ] Frontend scaffold displaying placeholder chat UI.
- [ ] Poetry environment configured with backend dependencies.
- [ ] Node.js environment with Tauri + React + TailwindCSS configured.
- [ ] Dummy test for backend `/health` endpoint passes.
- [ ] Dummy test for frontend component passes.

### Integration & Quality
- [ ] GitHub Actions workflow runs backend and frontend tests on push.
- [ ] Code follows project conventions and structure.
- [ ] Documentation updated with setup instructions.
- [ ] Tests written before implementation (TDD).

## Backend Requirements
- [ ] **Tests First**: Write failing test for `/health` endpoint.
- [ ] **TDD Notes**: Initial test checks for 200 OK and JSON `{"status": "ok"}`.
- [ ] **API Design**: `/health` GET endpoint returns status JSON.
- [ ] **Data Validation**: Not applicable for this endpoint.
- [ ] **Error Handling**: Endpoint always returns 200 unless server is down.
- [ ] **Documentation**: Add endpoint description in API docs.

## Frontend Requirements
- [ ] **Tests First**: Write failing test for rendering a placeholder chat component.
- [ ] **TDD Notes**: Component renders “Chat placeholder” text on load.
- [ ] **Component Design**: Minimal App component with placeholder chat box.
- [ ] **UI/UX**: Not applicable yet for design polish.
- [ ] **State Management**: Not applicable yet.
- [ ] **API Integration**: Not applicable yet.
- [ ] **Responsive**: Basic responsive layout with TailwindCSS classes.

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
[To be filled after completion:]
- **Files Created/Modified**: List of actual files with brief purpose
- **Key Technical Decisions**: Important choices made during implementation
- **API Endpoints**: `/health`
- **Components Created**: Placeholder Chat component
- **Challenges & Solutions**: Any significant problems encountered and how they were solved
- **Notes for Future Tasks**: Any setup choices that impact other tasks
