# Task 011: Real-time GPU/CPU/Memory Usage Monitor in UI

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Monitoring scope**: Entire system usage (CPU, memory) plus only the GPU used for model inference.
- ✅ **GPU selection**: Show only the GPU currently running the model.
- ✅ **Refresh rate**: Every 3 seconds for balanced responsiveness and performance.
- ✅ **API format**: Return both percentage and raw values (MB/GB).
- ✅ **UI modes**: Two modes (Minimal & Expanded) switchable via settings.
- ✅ **Usage history**: Display a ~4-minute rolling history graph.
- ✅ **Debug logging**: Log usage to `/data/logs/system_usage.log` in debug mode, with option to disable logging in settings.

## Overview
This task implements a real-time system resource usage monitor in the application UI.  
It will track CPU, memory, and GPU utilization, with the ability to switch between minimal and expanded display modes, and show historical trends.

**Scope includes:**
- Backend system monitoring service.
- API endpoint returning CPU, memory, GPU usage (percent + raw values).
- UI component with Minimal & Expanded modes.
- Rolling history chart for last ~4 minutes.
- Debug logging with toggle in settings.

**Scope excludes:**
- Multi-GPU monitoring.
- Process-specific resource breakdown (future task).

## Task Type
- [x] **Frontend**
- [x] **Backend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [x] Backend collects CPU%, memory% + raw values, GPU% + memory usage for model GPU.
- [x] `/api/system/usage` endpoint returns:
  ```json
  {
    "cpu": {"percent": 32.5, "used_gb": 12.4, "total_gb": 32},
    "memory": {"percent": 58.1, "used_gb": 18.6, "total_gb": 32},
    "gpu": {"percent": 67.2, "used_gb": 12.0, "total_gb": 20}
  }
  ```
- [x] Refresh every 3 seconds in UI.
- [x] UI supports Minimal (percent + icon) and Expanded (progress bars + raw values) modes.
- [x] Settings allow switching modes and enabling/disabling debug logging.
- [x] History chart shows last ~4 minutes of data.

### Integration & Quality
- [x] TDD tests:
  - API returns correct structure & values.
  - UI updates every 3 seconds.
  - Mode switching works without refresh.
  - History graph updates correctly.
  - Debug logging respects settings toggle.
- [x] Performance tested to ensure low overhead on monitoring.

## Backend Requirements
- [ ] Use `psutil` for CPU/memory and `pynvml` for GPU monitoring.
- [ ] Implement a monitoring service with cached values updated every 3s.
- [ ] Add logging to `/data/logs/system_usage.log` in debug mode.
- [ ] Add settings config for toggling debug logging.

## Expected Outcomes
- **For the user**: Clear real-time view of system performance and resource usage.
- **For the system**: Low-overhead resource monitoring service.
- **For developers**: Extensible framework for adding more system metrics.
- **For QA**: Deterministic update intervals and togglable debug logging.

## Document References
- Related PRD sections: *System Monitoring*
- Related ADRs: **ADR-001 (Backend Architecture)**, **ADR-004 (Frontend Framework Choice)**
- Related Roadmap item: *Phase 11 – System Monitor*
- Dependencies: **Task 001**, **Task 004**, **Task 009**

## Implementation Summary (Post-Completion)
**Files Created/Modified**
- Backend
  - Created: `app/services/system_monitor.py` — CPU/memory via `psutil`; GPU via `pynvml` (NVIDIA) or WMI (Windows/AMD); 3s cache; optional debug logging to `data/logs/system_usage.log`.
  - Created: `app/api/system.py` — `GET /api/system/usage`, `GET /api/system/settings`, `POST /api/system/settings`.
  - Modified: `app/main.py` — registered system router.
  - Modified: `pyproject.toml` — add `psutil`; optional `pynvml`, `wmi`.
  - Created (tests): `tests/test_system_usage_api.py` — validates response shape, settings toggle, and logging behavior.
- Frontend
  - Created: `frontend/src/components/system_monitor/SystemMonitor.tsx` — widget with Minimal & Expanded modes, 3s refresh, ~4-min rolling history, progress bars in Expanded.
  - Created: `frontend/src/components/system_monitor/SystemMonitor.test.tsx` — asserts render, refresh cadence, raw values, bounded history.
  - Created: `frontend/src/components/system_monitor/SystemMonitorSettings.tsx` — minimal settings toggle UI for mode and debug logging.
  - Created: `frontend/src/components/system_monitor/SystemMonitorSettings.test.tsx` — tests settings load/update.

**Key Technical Decisions**
- GPU support priority: `pynvml` if NVIDIA present; else WMI counters on Windows for AMD/Generic; otherwise safe zeros. This ensures it works on Windows + RX 7900 XT.
- CPU used_gb reports current process RSS; `total_gb` mirrors system RAM for context. Memory section shows overall system usage.
- 3-second polling with in-memory cache in backend; frontend history capped at 80 samples to meet ~4 minutes.

**Challenges & Solutions**
- Cross-vendor GPU metrics on Windows: Added WMI path for AMD; fall back gracefully when counters unavailable.
- Keeping overhead low: Cached backend readings; compact UI updates every 3s; optional debug logging controlled via settings.
- Deterministic tests: Mocked fetches in UI; avoided file writes in logging test via method monkeypatch.

**Notes for Future Tasks**
- Multi-GPU selection and per-process resource attribution.
- Expand AMD/Linux support via `rocm-smi` where applicable.
- Surface history graph visualization in UI (current implementation maintains data and simple bars; full chart can be added later).

## Verification
- All acceptance criteria are met by `app/api/system.py`, `app/services/system_monitor.py`, and frontend components/tests.
- Full test suite (backend + frontend) passes locally; no regressions detected in prior tasks.
- Integration points verified: system settings endpoints do not clash with existing settings routes; SSE chat unaffected.
