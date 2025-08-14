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
- [ ] Backend endpoints to retrieve and update settings (`/api/settings/global`, `/api/settings/session/{id}`).
- [ ] Database tables updated to store settings persistently (linking session settings to `session_id`).
- [ ] Frontend state management for switching between Basic and Advanced modes.
- [ ] TDD tests:
  - Create/update/read global settings.
  - Create/update/read session settings.
  - Ensure session overrides fall back to global values when unset.

## Backend Requirements
- [ ] Use database to store settings (SQLAlchemy models `GlobalSettings` and `SessionSettings`).
- [ ] Add config service for retrieving merged settings (session overrides > global).
- [ ] Provide endpoints for frontend to fetch and update settings.

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
[To be filled after completion:]
- **Files Created/Modified**: `app/api/settings.py`, `app/models/settings.py`, `frontend/components/settings/`
- **Key Technical Decisions**: Two-mode UI, persistent DB storage, tooltip-based parameter descriptions.
- **API Endpoints**: `GET/POST /api/settings/global`, `GET/POST /api/settings/session/{id}`
- **Components Created**: Global Settings panel, Local Session Settings UI.
- **Challenges & Solutions**: Ensuring seamless override behavior, user-friendly descriptions.
- **Notes for Future Tasks**: Add real-time preview of changes, role-based restrictions.
