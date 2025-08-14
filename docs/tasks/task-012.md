# Task 012: AI Internet Search Toggle

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Scope**: Use free and open search APIs — primary: DuckDuckGo Instant Answer API (no API key required), fallback: Bing Web Search if user provides API key.
- ✅ **Mode**: AI decides autonomously when to search; user can globally enable/disable search in settings.
- ✅ **Rate limit**: Max 13 searches per minute to avoid IP bans.
- ✅ **Backend search execution**: Direct HTTP requests from backend, parsing JSON/HTML results locally (no paid intermediaries).
- ✅ **Result usage**: Results are directly injected into model context (no separate display in chat).
- ✅ **Debug mode**: Log full search queries and responses to `/data/logs/search_debug.log` when enabled.

## Overview
This task implements a backend + UI feature allowing the AI to perform internet searches when needed, controlled by a toggle in settings.  
When enabled, the AI can retrieve fresh information from the web using free APIs and inject it into its context for better answers.

**Scope includes:**
- Backend integration with DuckDuckGo API, optional Bing fallback.
- Rate limiting (13 requests/minute).
- Global toggle in settings (enabled/disabled).
- Automatic AI decision to search when relevant.
- Debug logging for queries and responses.

**Scope excludes:**
- Rendering search results in UI (future task).
- User prompt confirmation before each search (future enhancement).

## Task Type
- [x] **Frontend**
- [x] **Backend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [ ] Global toggle in Settings for "Allow AI Internet Search".
- [ ] Backend service for performing searches via DuckDuckGo API.
- [ ] Optional Bing search if API key provided in settings.
- [ ] Rate limit of 13 searches/minute enforced server-side.
- [ ] AI pipeline automatically calls search service when relevant.
- [ ] Search results appended to prompt context before model call.
- [ ] Debug logging to `/data/logs/search_debug.log` when enabled.

### Integration & Quality
- [ ] TDD tests:
  - Search service returns valid results for sample queries.
  - Rate limiting prevents excessive queries.
  - Toggle disables search calls completely.
  - Debug logs contain correct data in debug mode.
- [ ] Performance testing to ensure minimal latency overhead.

## Backend Requirements
- [ ] Create `services/search_service.py` to handle DuckDuckGo & Bing API calls.
- [ ] Implement caching of search results for identical queries within 2 minutes.
- [ ] Add `/api/settings/search` endpoint to toggle and store config in DB.
- [ ] Integrate search results into RAG/context builder before model inference.

## Expected Outcomes
- **For the user**: Fresh, up-to-date information when AI is allowed to search.
- **For the system**: Secure, cost-free search capability with rate limiting.
- **For developers**: Modular search service with room for new engines in future.
- **For QA**: Easy toggle testing and verification via debug logs.

## Document References
- Related PRD sections: *AI Internet Search*
- Related ADRs: **ADR-001 (Backend Architecture)**, **ADR-004 (Frontend Framework Choice)**, **ADR-005 (RAG Architecture)**
- Related Roadmap item: *Phase 12 – Internet Search Integration*
- Dependencies: **Task 001**, **Task 004**, **Task 005**, **Task 008**, **Task 009**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `app/services/search_service.py`, `app/api/settings.py`
- **Key Technical Decisions**: Free API usage, rate limiting, auto-injection to context.
- **API Endpoints**: `GET /api/settings/search`, `POST /api/settings/search`
- **Components Created**: Settings toggle in UI.
- **Challenges & Solutions**: Avoiding API bans, keeping latency low.
- **Notes for Future Tasks**: Add UI display of search results, prompt user before search.
