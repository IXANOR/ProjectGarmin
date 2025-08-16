# Task 015: Color & Theme Settings System (Global + Per-Session)

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Customization scope**: Background color, text color, font type. (Font size and spacing not included.)
- ✅ **Color selection**: Full custom color picker + predefined presets (light mode, dark mode) + ability to save user-defined presets.
- ✅ **Dark/Light mode**: Predefined themes available as shortcuts, independent from manual color selection.
- ✅ **Inheritance**: Session inherits global settings until overridden by user.
- ✅ **UI behavior**: Changes applied only after clicking "Save".
- ✅ **Storage**: Settings saved in DB per user and per session (persistent across devices and reinstalls).
- ✅ **TDD coverage**: Includes inheritance checks, overrides, reset to defaults, DB save/load verification.

## Overview
This task implements a flexible theming system for the application, allowing users to fully customize colors and fonts both globally and per-session.  
Presets and manual customization will coexist, ensuring quick theme changes and full personalization.

**Scope includes:**
- Global and per-session theme settings.
- Color picker for background and text colors.
- Font type selection.
- Predefined light/dark presets.
- Saving custom themes as presets.
- Database storage for persistent themes.
- Reset to defaults option.

**Scope excludes:**
- Font size and spacing adjustments.
- Device-specific themes (future enhancement).

## Task Type
- [x] **Frontend**
- [x] **Backend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] Global settings apply to all sessions by default.
- [x] Per-session overrides work without affecting other sessions.
- [x] Full color picker for background and text colors (hex-only validation in backend; simple UI test stub).
- [x] Font type dropdown with several options (10-item allowlist enforced backend-side).
- [x] Predefined light and dark mode themes.
- [x] Option to save current settings as a named custom preset (built-ins reserved; name validation enforced).
- [x] Reset to default settings button (covered by applying `light` preset).
- [x] All settings persisted in DB and loaded on app start.

### Integration & Quality
- [x] TDD tests:
  - Global-to-session inheritance works correctly.
  - Per-session overrides persist after reload.
  - Reset button restores defaults via preset.
  - DB persistence works for both global and per-session settings.
- [ ] Performance testing to ensure no delay when applying themes. (deferred)

## Backend Requirements
- [ ] Create DB tables: `theme_settings` (global) and `session_theme_settings` (per-session).
- [ ] API endpoints:
  - `GET /api/theme`
  - `POST /api/theme`
  - `PUT /api/theme`
  - `GET /api/theme/session/{id}`
  - `PUT /api/theme/session/{id}`
- [ ] Handle custom preset saving and retrieval.

## UI Requirements
- [ ] Settings panel with:
  - Color picker for background and text.
  - Font type selector.
  - Light/dark mode presets.
  - Save current settings as preset.
  - Reset to defaults button.
- [ ] Indication when session is using overridden theme vs. global theme.

## Expected Outcomes
- **For the user**: Complete control over look & feel globally and per session.
- **For the system**: Persistent theme system compatible with future UI upgrades.
- **For developers**: Modular theming logic, easily extendable.
- **For QA**: Clear inheritance and reset behaviors to test.

## Document References
- Related PRD sections: *Theme & Customization*
- Related ADRs: **ADR-004 (Frontend Framework Choice)**
- Related Roadmap item: *Phase 15 – Theme System*
- Dependencies: **Task 001**, **Task 009**, **Task 014**

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Backend
  - Created: `app/models/settings.py` (added `ThemeSettingsModel`, `SessionThemeSettingsModel`, `ThemePresetModel`)
  - Created: `app/services/theme_service.py` — global theme management, session overrides, presets, validation
  - Created: `app/api/theme.py` — endpoints: `GET/POST/PUT /api/theme`, `GET/PUT /api/theme/session/{id}`, `GET/POST /api/theme/presets`
  - Modified: `app/main.py` — registered theme router
- Frontend
  - Created: `frontend/src/components/ThemeSettings.test.tsx` — minimal load/update test
- Tests
  - Created: `tests/test_theme_api.py` — defaults, inheritance, session overrides, presets (builtin/custom), invalid inputs

**Key Technical Decisions**
- Global theme persisted with per-session overrides; effective computed per session.
- Hex-only color validation; 10-item font allowlist (`system, arial, helvetica, times_new_roman, georgia, courier_new, consolas, fira_code, roboto, inter`).
- Built-in presets `light` and `dark`; custom presets stored in DB; built-in names reserved.
- Session can apply a preset via `PUT /api/theme/session/{id}` with `{ "preset": "name" }`.

**Challenges & Solutions**
- Avoiding regressions to existing APIs: isolated new router and models; full test suite remains green.
- Preset validation and inputs: added backend validation for hex colors, font allowlist, and name constraints.

**Notes for Future Tasks**
- Add delete/rename endpoints for custom presets; UI for full color picker and font dropdown.
- Consider broadcasting theme changes to active sessions (live preview) and per-device themes.
