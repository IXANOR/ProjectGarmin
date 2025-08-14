# Task 019: Final Integration & End-to-End Testing (RC1)

## Decisions Based on Your Inputs
- ✅ **Scope**: Integrate **all modules** (backend, frontend, DB, model inference, RAG, files, settings, personality, search, monitoring, history).
- ✅ **E2E strategy**: Two-tier tests
  - **Tier 1 – Mocked E2E (default/CI)**: All external dependencies mocked (model, OCR/STT, embeddings, Chroma, search). No side-effects on real data.
  - **Tier 2 – Live Smoke E2E (optional/manual)**: Runs with the **full model** and real services using temp data dirs; gated by env flag.
- ✅ **Tools**: Playwright (frontend flows) + pytest/httpx (backend/API). Coverage reported in CI.
- ✅ **Model in tests**: Full model used **only** in Tier 2 smoke; Tier 1 uses a deterministic streaming stub.
- ✅ **Release Candidate**: Produce **RC1** artifacts (Windows build + zipped portable), checksums, and release notes.
- ✅ **TDD approach**: Hybrid — write failing E2E for critical flows first, keep unit/integration tests for modules; add mocks to keep CI fast and deterministic.

---

## Overview
This task stitches the entire system together and validates it with end-to-end tests. It also prepares the first **Release Candidate (RC1)** for distribution on Windows.

**Scope includes:**
- Wiring all modules and verifying data flow front↔back↔DB↔vector store.
- E2E suites (mocked + optional live smoke).
- RC packaging scripts and release notes.
- CI pipelines to run Tier 1 by default and allow Tier 2 via flag.

**Scope excludes:**
- Performance benchmarking (future task).
- Linux/macOS packaging (future task).

## Acceptance Criteria
### Functional E2E (Tier 1 – Mocked, CI)
- [ ] **Chat flow**: User sends message → SSE stream renders → reply appears (model mocked).
- [ ] **RAG PDF**: Upload PDF → chunks embedded (mock) → retrieval affects reply → citations appear.
- [ ] **Images**: Upload image → OCR (mock) → retrieval works.
- [ ] **Audio**: Upload audio → transcription (mock) → retrieval works with segment metadata.
- [ ] **Multi-source**: Mixed retrieval ranks by similarity; `sources` filter respected.
- [ ] **Sessions & persistence**: Create/list/get/delete sessions; history persists in SQLite temp DB.
- [ ] **Settings**: Global and per-session overrides applied (model params, theme, personality, search toggle).
- [ ] **Personality**: Changing profile impacts tone in stubbed replies (assert via tags/markers).
- [ ] **Search**: When enabled, mocked search adds snippets to context; when disabled, no calls.
- [ ] **Context trimming**: Trigger summarization (mock), knowledge capture stored & injected when relevant.
- [ ] **File manager**: Upload/list/reprocess/reassign; soft vs hard delete behavior verified.
- [ ] **Monitoring**: UI renders mocked metrics and 4–10 min history graph.
- [ ] **Logging**: Messages and metadata written to conversation logs; export JSON/CSV works.

### Functional E2E (Tier 2 – Live Smoke, manual)
- [ ] Same core flows but with **real** model + embeddings + Chroma + OCR/STT + search (if keys present).
- [ ] Uses **temp** dirs: `/tmp_app/data` (Windows: `%TMP%\app_data`) and temporary SQLite DB; leaves no residue.
- [ ] Executes under `E2E_LIVE=1` (env flag) and times out gracefully if model unavailable.

### Quality & CI
- [ ] Playwright tests run headless in CI; screenshots/videos saved on failure.
- [ ] Pytest runs API/integration tests with mocks; coverage > **80%** for critical modules.
- [ ] Job matrix: `e2e-mocked` (default) + `e2e-live` (manual trigger).
- [ ] All tests deterministic (fixed seeds, stable stubs).

### Release Candidate (RC1)
- [ ] Build Windows executable/portable:
  - **PyInstaller** for backend service
  - Frontend production build
  - Packaging script bundles runtime, config templates, and README
- [ ] Checksums (SHA256) generated for artifacts.
- [ ] Release notes: features, known issues, setup steps, system requirements.
- [ ] Smoke run script validates startup, sample chat, and graceful shutdown.

## Test Design (TDD Notes)
- **Model stub**: Deterministic stream (`["Hello","from","mock","AI"]`) with hooks for tone/citations.
- **RAG stub**: Returns fixed chunks with `source_type`, metadata, and scores.
- **OCR/STT stubs**: Deterministic text for given sample assets.
- **Chroma stub**: In-memory fake implementing `query/add/delete`.
- **Search stub**: Returns fixed URLs/snippets based on query patterns.
- **Metrics stub**: Fixed waveforms for GPU/CPU/RAM/Disk.
- Use fixtures to isolate temp dirs and DB per test; ensure cleanup.

## Implementation Plan
1. **Stubs & fixtures**: Implement service mocks; config switches to route real vs mocked services.
2. **Playwright E2E**: Flows for chat, upload, retrieval, settings, manager, monitoring.
3. **Backend E2E**: Pytest scenarios for APIs, context builder, trimming/knowledge.
4. **RC packaging**: PyInstaller spec, frontend build, bundle scripts, README.
5. **CI wiring**: GitHub Actions workflows for `e2e-mocked` (default) and `e2e-live` (manual).
6. **Docs**: `docs/TESTING.md` for running both tiers; `docs/RELEASE_NOTES_RC1.md` template.

## Backend/Infra Requirements
- [ ] Config flags: `USE_MOCKS`, `E2E_LIVE`, `DATA_DIR`, `DB_URL`.
- [ ] Temp dirs and DB auto-created & cleaned after tests.
- [ ] PyInstaller spec for Windows build.
- [ ] Playwright & pytest setup scripts.

## Expected Outcomes
- **For the user**: A cohesive app that runs end-to-end and a downloadable RC1 build.
- **For the system**: Verified integration paths and stable CI.
- **For developers**: Clear patterns for mocks vs real services; reproducible E2E.
- **For QA**: Deterministic, automatable checks with optional live validation.

## Document References
- Related PRD: *MVP scope, RAG, Settings, Personality, Monitoring, History*
- Related ADRs: **ADR-001**, **ADR-003**, **ADR-004**, **ADR-005**, **ADR-006**
- Related Roadmap: *Final integration & release*
- Dependencies: Tasks **001–018**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `e2e/` tests, `scripts/build_win.ps1`, `scripts/run_smoke.ps1`
- **Key Technical Decisions**: Two-tier E2E, RC packaging, CI matrix.
- **Artifacts**: RC1 executables/zips, checksums, release notes.
- **Challenges & Solutions**: Flaky E2E handling, stable mocks, packaging quirks on Windows.
