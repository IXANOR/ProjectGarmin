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
- [ ] Backend collects CPU%, memory% + raw values, GPU% + memory usage for model GPU.
- [ ] `/api/system/usage` endpoint returns:
  ```json
  {
    "cpu": {"percent": 32.5, "used_gb": 12.4, "total_gb": 32},
    "memory": {"percent": 58.1, "used_gb": 18.6, "total_gb": 32},
    "gpu": {"percent": 67.2, "used_gb": 12.0, "total_gb": 20}
  }
  ```
- [ ] Refresh every 3 seconds in UI.
- [ ] UI supports Minimal (percent + icon) and Expanded (progress bars + raw values) modes.
- [ ] Settings allow switching modes and enabling/disabling debug logging.
- [ ] History chart shows last ~4 minutes of data.

### Integration & Quality
- [ ] TDD tests:
  - API returns correct structure & values.
  - UI updates every 3 seconds.
  - Mode switching works without refresh.
  - History graph updates correctly.
  - Debug logging respects settings toggle.
- [ ] Performance tested to ensure low overhead on monitoring.

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
[To be filled after completion:]
- **Files Created/Modified**: `app/services/system_monitor.py`, `app/api/system.py`, `frontend/components/system_monitor/`
- **Key Technical Decisions**: Chosen refresh rate, dual UI modes, 4-minute history.
- **API Endpoints**: `GET /api/system/usage`
- **Components Created**: System monitor widget with two display modes and history graph.
- **Challenges & Solutions**: Minimizing performance impact, ensuring accurate GPU detection.
- **Notes for Future Tasks**: Add multi-GPU monitoring, process-specific stats.
