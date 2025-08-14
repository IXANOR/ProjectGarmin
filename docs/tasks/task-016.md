# Task 016: Unified Global & Local Settings Panel

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Global panel scope**: Includes Theme & Colors (Task 015), Model Parameters (Task 009), Personality (Task 014), AI Internet Search Toggle (Task 012), Default RAG Settings (limits, OCR/STT languages), Debug Mode (Task 010).
- ✅ **Local session panel scope**: Includes overrides for Theme/Colors, Model Parameters, Personality. RAG and integrations remain global only for now.
- ✅ **UI layout**: Tabbed interface (e.g., Appearance, AI Settings, Integrations, Advanced).
- ✅ **Saving behavior**: Includes "Apply without saving" for testing and "Save changes" for DB persistence.
- ✅ **Global settings sync**: Changes in global settings immediately update all sessions that don't have overrides.
- ✅ **TDD coverage**: Tests for inheritance, overrides, conflict resolution (local overrides win), and instant global sync.

## Overview
This task creates a unified, user-friendly panel that consolidates all global and local settings into one central UI location.  
It merges theming, AI model parameters, personality, and integration toggles for easy management and visibility.

**Scope includes:**
- Global settings panel with tabs for organized configuration.
- Local session settings accessible from chat view for overrides.
- Apply/Save functionality for safe testing.
- DB integration for persistent settings storage.
- Real-time sync of global settings to active sessions without overrides.

**Scope excludes:**
- Per-device settings (future enhancement).
- Bulk editing of settings for multiple sessions (future enhancement).

## Task Type
- [x] **Frontend**
- [x] **Backend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [ ] Tabbed global settings panel with sections:
  - Appearance (Theme, Colors, Fonts, Presets)
  - AI Settings (Model Parameters, Personality)
  - Integrations (AI Internet Search toggle, Default RAG settings)
  - Advanced (Debug mode, performance options)
- [ ] Local session settings panel in chat view with:
  - Theme/Colors overrides
  - Model Parameter overrides
  - Personality overrides
- [ ] "Apply without saving" button for temporary changes.
- [ ] "Save changes" button that persists to DB.
- [ ] Global changes immediately sync to all sessions without overrides.
- [ ] Overrides remain unaffected by global changes.

### Integration & Quality
- [ ] TDD tests:
  - Inheritance of global settings to new sessions.
  - Correct application of local overrides.
  - Conflict resolution (local > global).
  - Instant global settings sync.
- [ ] UI tests for tab navigation and live preview of "Apply without saving".

## Backend Requirements
- [ ] Extend DB schema to unify settings storage in `global_settings` and `session_settings` tables.
- [ ] API endpoints:
  - `GET /api/settings/global`
  - `PUT /api/settings/global`
  - `GET /api/settings/session/{id}`
  - `PUT /api/settings/session/{id}`
- [ ] WebSocket or event-based system to push global setting changes to active sessions.

## UI Requirements
- [ ] Create tabbed settings interface in frontend.
- [ ] Integrate color pickers, sliders, and toggles for relevant settings.
- [ ] "Apply without saving" applies changes locally for preview only.
- [ ] Indication in UI when session is using overrides vs. global defaults.

## Expected Outcomes
- **For the user**: Centralized and intuitive control over all settings.
- **For the system**: Simplified settings management with clear precedence rules.
- **For developers**: Single framework for managing settings, reducing duplication.
- **For QA**: Clear scenarios for testing inheritance, overrides, and sync.

## Document References
- Related PRD sections: *Settings & Customization*
- Related ADRs: **ADR-004 (Frontend Framework Choice)**, **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 16 – Unified Settings Panel*
- Dependencies: **Task 009**, **Task 012**, **Task 014**, **Task 015**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `frontend/components/settings_panel/`, `app/db/settings.py`
- **Key Technical Decisions**: Tabbed interface, dual Apply/Save system, instant sync mechanism.
- **API Endpoints**: Listed above.
- **Components Created**: Global settings panel, Local session settings panel.
- **Challenges & Solutions**: Ensuring consistent inheritance, handling conflicts smoothly.
- **Notes for Future Tasks**: Extend to per-device settings and bulk edits.
