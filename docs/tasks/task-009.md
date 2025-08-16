# Task 009: Model Parameter Configuration UI

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Parameters in UI**: Basic set (`temperature`, `top_p`, `max_tokens`, `presence_penalty`, `frequency_penalty`) in Basic mode; all advanced parameters (e.g., `stop_sequences`, `repetition_penalty`) in Advanced mode.
- ✅ **UI Modes**: Two modes — Basic (limited parameters, safe defaults) and Advanced (full list of parameters, with descriptions).
- ✅ **Validation**: No hard validation, but display recommended ranges for each parameter.
- ✅ **Scope of settings**: Global defaults in a dedicated **Settings** panel; per-session overrides in **Local Session Settings**.
- ✅ **Default values**: Keep safe defaults for Basic mode (temperature=0.7, top_p=1.0, max_tokens=1024, presence_penalty=0, frequency_penalty=0).
- ✅ **UI placement**: Global settings in a separate panel; local settings accessible from chat view.
- ✅ **Saving settings**: Save only after clicking **Save Changes**.

## Overview
This task implements a user interface for configuring model inference parameters both globally and per chat session.  
The UI will have two modes: Basic (for non-technical users) and Advanced (for technical users who want full control).  
Settings can be overridden per session and are stored persistently.

**Scope includes:**
- Basic mode with essential parameters and safe defaults.
- Advanced mode with all available parameters, each with a description.
- Global settings accessible from main Settings panel.
- Per-session overrides accessible from within a chat session.
- Persistent storage of settings in the database (global and per-session).
- Recommended range display for each parameter.
- Save changes only when the user clicks the button.

**Scope excludes:**
- Real-time preview of parameter effects (future task).
- User role-based restrictions for parameter changes (future task).

## Task Type
- [x] **Frontend**
- [x] **Backend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [ ] **Global settings**: Accessible in Settings panel, updates saved to DB.
- [ ] **Local session settings**: Accessible in chat view, overrides global settings for that session.
- [ ] **Basic mode**: Displays `temperature`, `top_p`, `max_tokens`, `presence_penalty`, `frequency_penalty`.
- [ ] **Advanced mode**: Displays all parameters including advanced ones.
- [ ] **Parameter descriptions**: Each parameter has a tooltip or info icon explaining its function.
- [ ] **Recommended ranges**: Displayed alongside parameter input fields.
- [ ] **Save changes** button required to commit changes.

### Integration & Quality
- [x] Backend endpoints to retrieve and update settings (`/api/settings/global`, `/api/settings/session/{id}`).
- [x] Database tables updated to store settings persistently (linking session settings to `session_id`).
- [ ] Frontend state management for switching between Basic and Advanced modes.
- [x] TDD tests:
  - Create/update/read global settings.
  - Create/update/read session settings.
  - Ensure session overrides fall back to global values when unset.

## Backend Requirements
- [x] Use database to store settings (SQLModel tables `GlobalSettingsModel` and `SessionSettingsModel`).
- [x] Add retrieval/merge logic where session overrides > global (implemented in settings API GET handler).
- [x] Provide endpoints for frontend to fetch and update settings.

## Expected Outcomes
- **For the user**: Easy-to-use interface for controlling AI behavior globally or per chat.
- **For the system**: Persistent configuration management that integrates directly with model inference pipeline.
- **For developers**: Structured settings storage, making it easy to add new parameters in the future.
- **For QA**: Clear separation between global and session-specific settings.

## Document References
- Related PRD sections: *Model Parameter Configuration*
- Related ADRs: **ADR-001 (Backend Architecture)**, **ADR-004 (Frontend Framework Choice)**, **ADR-005 (RAG Architecture)**
- Related Roadmap item: *Phase 9 – Model Parameter UI*
- Dependencies: **Task 001**, **Task 004**, **Task 005**, **Task 008**

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Created (backend):
  - `app/api/settings.py` — REST endpoints for global and session settings
  - `app/models/settings.py` — SQLModel tables: `GlobalSettingsModel`, `SessionSettingsModel`
  - `tests/test_settings_api.py` — TDD tests for global and session CRUD/merge behavior
- Modified:
  - `app/main.py` — registered settings router under prefix `/api`

**Key Technical Decisions**
- Store global defaults in a single-row table (`GlobalSettingsModel`, id=1) for simplicity.
- Store per-session overrides as JSON in `SessionSettingsModel.overrides_json` (only provided keys persisted).
- Whitelist handled parameters for MVP: `temperature`, `top_p`, `max_tokens`, `presence_penalty`, `frequency_penalty`.
- Effective settings are computed as: session overrides > global defaults. Returned shape: `{ session_id, effective, overrides }`.
- Endpoints are idempotent POST updates for simplicity; validation kept minimal in MVP.

**API Endpoints**
- `GET /api/settings/global` → returns global defaults
- `POST /api/settings/global` → partial update of global defaults
- `GET /api/settings/session/{id}` → returns `{ session_id, effective, overrides }`
- `POST /api/settings/session/{id}` → partial update of per-session overrides

**Components Created**
- Backend only in this task. Frontend UI will be added in a follow-up.

**Challenges & Solutions**
- Ensuring deterministic defaults when no rows exist → lazy creation of the global settings row on first access.
- Non-breaking integration with existing APIs → isolated router under `/api/settings`, no changes to chat/files endpoints.
- Clear override precedence → merged in API handler and covered by tests.

**Notes for Future Tasks**
- Implement frontend Settings UI (Basic/Advanced) consuming these endpoints.
- Consider advanced parameters and validation ranges surfaced via the API.
- Add push-notify (WebSocket/SSE) so active sessions can react to global changes.
- Wire settings into model invocation once model integration replaces the mock stream.
- Provide `.env.example` and load `.env` in `dev.ps1` for local overrides.
- Inference integration plan: use **LM Studio** as the local inference provider (OpenAI-compatible server on `http://127.0.0.1:<PORT>`). The backend will:
  - Forward model parameters from these settings on each call
  - Health‑check the endpoint and, if unavailable, prompt/attempt to start LM Studio minimized
  - Document recommended LM Studio setup: enable “Start OpenAI server on launch” and “Start minimized to tray”, bind to the chosen model preset
  - Add envs for host/port/model name (e.g., `LLM_HOST`, `LLM_PORT`, `LLM_MODEL`)
