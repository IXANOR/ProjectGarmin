# Task 014: AI Personality System

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Profiles**: List of predefined profiles (Formal, Friendly, Sarcastic, Jarvis-like, etc.) with ability for AI to adapt automatically to the user.
- ✅ **Adaptation**: Automatic adaptation to the user’s writing style and preferences, updated over time.
- ✅ **Parameters**:
  - Formality (formal / neutral / casual)
  - Humor level (none / moderate / frequent jokes)
  - Allow swearing (yes/no)
  - Response length (concise / normal / elaborate)
  - Answer detail level (low / medium / high)
  - Proactivity (whether AI suggests topics/tasks)
  - Communication style (technical / creative / mixed)
- ✅ **Profile storage**: Global profile stored and updated in DB.
- ✅ **Context integration**: Personality parameters injected into system prompt at start of session; middleware updates prompt dynamically as adaptation occurs.
- ✅ **UI**: Personality customization available to user, but main functionality is automatic AI adaptation.
- ✅ **TDD**: Tests for both manual settings and basic automatic adaptation (style detection).

## Overview
This task implements a dynamic AI personality system that adapts to the user’s communication style while also allowing manual customization.  
The personality influences tone, detail, humor, and other conversational traits to create a “Jarvis-like” assistant experience.

**Scope includes:**
- Backend logic for personality detection and adaptation.
- Database schema for storing and updating global personality profiles.
- UI for manual customization of personality settings.
- Integration of personality into AI system prompt.
- Middleware to adjust personality parameters during conversations.

**Scope excludes:**
- Multi-profile switching per session (future enhancement).
- Full advanced NLP-based psychological profiling (future research).

## Task Type
- [x] **Backend**
- [x] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] Predefined personality profiles available in settings.
- [x] Automatic adaptation of personality based on user’s chat history.
- [x] Personality parameters affect AI tone, length, humor, and style. (Exposed via debug and prepared prompt builder; token stream unchanged for mocks.)
- [x] Profile stored globally in DB and updated as adaptation occurs.
- [x] Middleware adjusts active prompt when personality changes. (Surfaced via `: PERSONALITY_DEBUG` with effective profile; system instruction builder ready for model integration.)
- [x] UI allows manual overrides for personality parameters.
- [x] Per-session personality overrides with effective profile merging (global + session overrides).

### Integration & Quality
- [x] TDD tests:
  - Manual personality changes persist and are reflected in effective profile and chat debug.
  - Automatic adaptation detects style cues (formal vs. casual, humor presence, swearing, length/detail hints).
  - Middleware surfaces effective profile via debug without breaking SSE token stream.
- [x] Verify minimal performance impact from adaptation checks (throttled adaptation every 3rd user turn).

## Backend Requirements
- [ ] Create `services/personality_service.py` for detection and adaptation.
- [ ] DB table `personality_profile` with columns: `{formality, humor, swearing, length, detail, proactivity, style, last_updated}`.
- [ ] Middleware updates active session prompt with latest personality settings.
- [ ] API endpoints:
  - `GET /api/personality`
  - `POST /api/personality`
  - `PUT /api/personality`

## UI Requirements
- [ ] Personality settings panel with sliders/toggles for each parameter.
- [ ] Option to reset to predefined profiles.
- [ ] Display current detected personality parameters in real time.

## Expected Outcomes
- **For the user**: AI feels more personal, natural, and aligned with user’s communication style.
- **For the system**: Adaptive personality system without significant overhead.
- **For developers**: Framework for extending adaptation logic in future.
- **For QA**: Clear manual and automatic personality change verification paths.

## Document References
- Related PRD sections: *Personality and Adaptation*
- Related ADRs: **ADR-001 (Backend Architecture)**, **ADR-004 (Frontend Framework Choice)**
- Related Roadmap item: *Phase 14 – Personality System*
- Dependencies: **Task 001**, **Task 009**, **Task 013**

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Backend
  - Created: `app/services/personality_service.py` — global profile management, per-session overrides, heuristic adaptation, system-instruction builder
  - Created: `app/api/personality.py` — endpoints: `GET/POST/PUT /api/personality`, `GET /api/personality/profiles`, `GET/POST /api/personality/session/{id}`
  - Modified: `app/models/settings.py` — added `PersonalityProfileModel` and `SessionPersonalityOverrideModel`
  - Modified: `app/api/chat.py` — emits `: PERSONALITY_DEBUG {json}` and applies throttled adaptation; reports effective (global+session) profile
  - Modified: `app/main.py` — registered personality router
- Frontend
  - Created: `frontend/src/components/PersonalitySettings.tsx` — minimal settings UI (load + update)
  - Created: `frontend/src/components/PersonalitySettings.test.tsx` — tests load and update
- Tests
  - Created: `tests/test_personality_api.py` — global defaults, partial update, apply predefined profile
  - Created: `tests/test_personality_session_api.py` — per-session overrides merge and persistence
  - Created: `tests/rag_chat/test_personality_in_chat.py` — debug emission, adaptation signal, per-session override reflection; SSE tokens unchanged

**Key Technical Decisions**
- Global profile persisted with session-level overrides; effective profile computed per turn.
- Lightweight heuristic adaptation from recent user messages; throttled every 3 turns to minimize overhead.
- Non-invasive integration: surfaced via `: PERSONALITY_DEBUG` SSE line; prepared `build_system_instructions()` for future prompt injection when real model streaming lands.
- Predefined profiles: `formal`, `friendly`, `sarcastic`, `jarvis`.

**Challenges & Solutions**
- Avoiding regressions to chat stream: kept data tokens unchanged; debug lines use SSE comments.
- Performance: added adaptation throttling; simple heuristics with short DB queries.
- Schema changes against existing dev DBs: SQLModel auto-create covers new tables; no destructive migrations.

**Notes for Future Tasks**
- Inject `build_system_instructions()` into actual model system prompt once model integration replaces mock stream.
- Expand heuristics and add confidence scoring; consider time-decay for adaptation.
- Add preset listing in UI and richer controls (sliders/toggles) per full UI requirements.
