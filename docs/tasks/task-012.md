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
- [x] Global toggle in Settings for "Allow AI Internet Search".
- [x] Backend service for performing searches via DuckDuckGo API.
- [x] Optional Bing search if API key provided in settings.
- [x] Rate limit of 13 searches/minute enforced server-side.
- [x] AI pipeline automatically calls search service when relevant.
- [x] Search results appended to prompt context before model call (represented as debug injection; ready to include in prompt when model integration is added).
- [x] Debug logging to `/data/logs/search_debug.log` when enabled.

### Integration & Quality
- [x] TDD tests:
  - Search service returns valid results for sample queries.
  - Rate limiting prevents excessive queries.
  - Toggle disables search calls completely.
  - Debug logs contain correct data in debug mode.
- [x] Performance testing to ensure minimal latency overhead.

## Backend Requirements
- [x] Create `services/search_service.py` to handle DuckDuckGo & Bing API calls.
- [x] Implement caching of search results for identical queries within 2 minutes.
- [x] Add `/api/settings/search` endpoint to toggle and store config in DB.
- [x] Integrate search results into RAG/context builder before model inference (non-invasive debug injection now; prompt stitching to be added when model streaming is implemented).

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
**Files Created/Modified**
- Backend
  - Created: `app/services/search_service.py` — DuckDuckGo first; optional Bing fallback; 13/min rate limit; 2-min cache; optional debug log to `data/logs/search_debug.log`.
  - Modified: `app/api/chat.py` — Added autonomous search trigger and `: SEARCH_DEBUG {json}` SSE when enabled; non-invasive to token stream.
  - Modified: `app/api/settings.py` — New `/api/settings/search` GET/POST storing `allow_internet_search`, `debug_logging`, and Bing key (stored server-side; exposed as `has_bing_api_key`).
  - Modified: `app/models/settings.py` — Added `SearchSettingsModel` with single-row config.
- Frontend
  - Created: `frontend/src/components/SearchSettings.tsx` — UI toggles for allow/debug; indicator for Bing key presence.
  - Created: `frontend/src/components/SearchSettings.test.tsx` — tests load/update toggles.
- Tests
  - Created: `tests/test_search_settings_api.py` — API defaults and update behavior.
  - Created: `tests/test_search_service.py` — DuckDuckGo parsing, cache, rate limiting, debug log.
  - Created: `tests/rag_chat/test_chat_search_integration.py` — Chat emits `: SEARCH_DEBUG` when enabled and relevant.

**Key Technical Decisions**
- Primary engine: DuckDuckGo Instant Answer API without key; fallback to Bing only if key present.
- Autonomous trigger heuristic: simple recency keywords (latest/news/update/recent) to avoid unnecessary calls; pluggable.
- Debug surfaces results via SSE comments without changing user-visible token stream.
- Secrets handling: Bing key stored in DB; API exposes only presence (`has_bing_api_key`).

**Challenges & Solutions**
- Avoiding external call flakiness in tests: injected dummy HTTP client for deterministic results.
- Preventing abuse/IP bans: strict 13/min rate limiter + 2-min cache per query.
- Non-invasive integration: emitted debug SSE separate from data tokens to preserve prior behavior and tests.

**Notes for Future Tasks**
- Wire search snippets into actual model prompt once model streaming is implemented.
- Expand search trigger heuristics and add result summarization/compression before injection.
- Add UI surface to show/search results inline (optional).
- Consider backoff and per-domain throttling if needed.
