# Task 018: Performance Monitoring & System Diagnostics

## Questions for Stakeholder/Owner (Decisions Taken)
- ✅ **Metrics scope**: GPU, CPU, RAM, Disk usage (no temperatures).
- ✅ **Data sources**: Only the GPU/CPU on which the model is running.
- ✅ **Refresh rate**: Every 5–7 seconds (consistent with Task 011) to balance responsiveness and performance.
- ✅ **History view**: Display historical usage graphs (5–10 minutes window).
- ✅ **Advanced mode**: Shows additional detailed metrics for GPU/CPU/RAM/Disk without process lists (future enhancement).
- ✅ **Logging**: Option to save performance data to CSV for debugging or analysis.
- ✅ **TDD coverage**: Mocked data sources for testing without requiring GPU load.

## Overview
This task adds a performance monitoring system to the application, allowing the user to track GPU, CPU, RAM, and Disk usage directly from the UI.  
It will feature a basic view (compact indicators) and an advanced view (historical graphs and detailed metrics).

**Scope includes:**
- Backend service for collecting performance metrics.
- UI component to display real-time usage and history graphs.
- Advanced mode toggle for more detailed metrics.
- CSV export/logging for debugging.

**Scope excludes:**
- Temperature monitoring.
- Process list with per-process resource usage.

## Task Type
- [x] **Backend**
- [x] **Frontend**
- [x] **Integration**

## Acceptance Criteria
### Core Functionality
- [ ] Collect metrics for GPU, CPU, RAM, and Disk usage.
- [ ] Refresh metrics every 5–7 seconds.
- [ ] Store up to 10 minutes of history for graph display.
- [ ] Provide basic and advanced modes in UI.
- [ ] Advanced mode shows detailed per-metric breakdowns (no process list).
- [ ] Option to enable/disable CSV logging of metrics in settings.
- [ ] Data collection only for GPU/CPU running the model.

### Integration & Quality
- [ ] TDD tests with mocked metrics sources.
- [ ] Verify accuracy of displayed metrics against system tools.
- [ ] Ensure CSV logs contain timestamped entries and correct formatting.

## Backend Requirements
- [ ] Implement metrics collection service using libraries like `psutil` (CPU, RAM, Disk) and `pynvml`/`rocm-smi` (GPU).
- [ ] API endpoints:
  - `GET /api/performance/current` → returns latest metrics.
  - `GET /api/performance/history` → returns last 10 minutes of metrics.
  - `POST /api/performance/logging` → enable/disable logging.
- [ ] CSV logging service with timestamped metrics.

## UI Requirements
- [ ] Compact performance indicators (GPU %, CPU %, RAM %, Disk %).
- [ ] Advanced panel with historical graphs.
- [ ] Toggle between basic and advanced view.
- [ ] CSV export button (if logging enabled).

## Expected Outcomes
- **For the user**: Clear visibility of system resource usage while running the model.
- **For the system**: Minimal overhead while collecting metrics.
- **For developers**: Easily extendable metrics framework.
- **For QA**: Mock-based tests to validate UI and API behavior.

## Document References
- Related PRD sections: *System Monitoring*
- Related ADRs: **ADR-001 (Backend Architecture)**
- Related Roadmap item: *Phase 18 – Performance Monitoring*
- Dependencies: **Task 011**

## Implementation Summary (Post-Completion)
[To be filled after completion:]
- **Files Created/Modified**: `services/metrics_service.py`, `frontend/components/performance_panel/`
- **Key Technical Decisions**: Use of `psutil` and GPU vendor-specific APIs.
- **API Endpoints**: Listed above.
- **Components Created**: Performance panel UI, advanced view graphs.
- **Challenges & Solutions**: Balancing refresh rate with performance overhead.
- **Notes for Future Tasks**: Possible addition of temperature and per-process monitoring.
