from __future__ import annotations

import json
import os
import time
from pathlib import Path
import platform
from typing import Any, Dict

try:  # Optional dependency; code must work without GPU libs
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

try:  # Optional, only if NVIDIA GPU available
    import pynvml  # type: ignore
    _HAS_NVML = True
except Exception:  # pragma: no cover
    pynvml = None  # type: ignore
    _HAS_NVML = False

try:  # Optional, Windows WMI for AMD/Generic GPU counters
    import wmi  # type: ignore
    _HAS_WMI = True
except Exception:  # pragma: no cover
    wmi = None  # type: ignore
    _HAS_WMI = False


class SystemMonitor:
    """Collects CPU, memory, and (if available) GPU usage.

    Values are cached for a short interval to reduce overhead.
    """

    def __init__(self, refresh_interval_seconds: float = 3.0, log_path: str | Path = "data/logs/system_usage.log") -> None:
        self.refresh_interval_seconds = refresh_interval_seconds
        self.log_path = Path(log_path)
        self._last_update_ts: float = 0.0
        self._last_snapshot: Dict[str, Any] | None = None
        # Settings managed via API
        self.mode: str = "minimal"  # "minimal" or "expanded"
        self.debug_logging: bool = False

        # Initialize NVML lazily when first needed
        self._nvml_inited: bool = False

    def get_settings(self) -> dict:
        return {"mode": self.mode, "debug_logging": self.debug_logging}

    def update_settings(self, *, mode: str | None = None, debug_logging: bool | None = None) -> dict:
        if mode is not None:
            mode_l = mode.lower()
            if mode_l not in {"minimal", "expanded"}:
                mode_l = "minimal"
            self.mode = mode_l
        if debug_logging is not None:
            self.debug_logging = bool(debug_logging)
        return self.get_settings()

    def get_usage(self) -> dict:
        now = time.time()
        if self._last_snapshot is not None and (now - self._last_update_ts) < self.refresh_interval_seconds:
            return self._last_snapshot

        snapshot = {
            "cpu": self._read_cpu(),
            "memory": self._read_memory(),
            "gpu": self._read_gpu(),
        }
        self._last_snapshot = snapshot
        self._last_update_ts = now
        self._maybe_log(snapshot)
        return snapshot

    def _read_cpu(self) -> dict:
        percent = 0.0
        if psutil is not None:
            try:
                # Non-blocking; first call may be 0.0 which is acceptable for UI
                percent = float(psutil.cpu_percent(interval=None))
            except Exception:
                percent = 0.0
        return {"percent": percent, "used_gb": self._read_process_memory_gb(), "total_gb": self._read_total_memory_gb()}

    def _read_memory(self) -> dict:
        used_gb = 0.0
        total_gb = 0.0
        percent = 0.0
        if psutil is not None:
            try:
                vm = psutil.virtual_memory()
                used_gb = float(vm.used) / (1024 ** 3)
                total_gb = float(vm.total) / (1024 ** 3)
                percent = float(vm.percent)
            except Exception:
                pass
        return {"percent": percent, "used_gb": round(used_gb, 2), "total_gb": round(total_gb, 2)}

    def _read_gpu(self) -> dict:
        # Default to zeros if no GPU API available
        percent = 0.0
        used_gb = 0.0
        total_gb = 0.0

        if _HAS_NVML:
            try:
                if not self._nvml_inited:
                    pynvml.nvmlInit()
                    self._nvml_inited = True
                # Simple heuristic: pick the first GPU. Future: choose the one used for model inference.
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                used_gb = float(mem.used) / (1024 ** 3)
                total_gb = float(mem.total) / (1024 ** 3)
                percent = float(util.gpu)
            except Exception:
                percent = 0.0
                used_gb = 0.0
                total_gb = 0.0
        # Windows AMD/Generic via WMI performance counters
        elif _HAS_WMI and platform.system().lower() == "windows":
            try:
                # Total VRAM from VideoController (bytes)
                c = wmi.WMI(namespace="root\\CIMV2")
                adapters = c.Win32_VideoController()
                # Choose first adapter
                if adapters:
                    try:
                        total_bytes = int(getattr(adapters[0], "AdapterRAM", 0) or 0)
                        total_gb = float(total_bytes) / (1024 ** 3)
                    except Exception:
                        total_gb = 0.0
                # Utilization from GPU Engine counters
                # Sum utilization across engines but clamp to 100
                engines = c.Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine()
                util_sum = 0.0
                for e in engines:
                    try:
                        util_sum += float(getattr(e, "UtilizationPercentage", 0.0) or 0.0)
                    except Exception:
                        pass
                if util_sum > 100.0:
                    util_sum = 100.0
                percent = util_sum
                # Memory usage from GPU memory perf counters if available
                try:
                    mem_counters = c.Win32_PerfFormattedData_GPUPerformanceCounters_Memory()
                    # DedicatedUsage likely in bytes; sum across instances
                    used_bytes = 0.0
                    for m in mem_counters:
                        try:
                            used_bytes += float(getattr(m, "DedicatedUsage", 0.0) or 0.0)
                        except Exception:
                            pass
                    used_gb = used_bytes / (1024 ** 3)
                except Exception:
                    # Fallback unknown; keep zero
                    pass
            except Exception:
                percent = 0.0
                used_gb = 0.0
                total_gb = 0.0

        return {"percent": percent, "used_gb": round(used_gb, 2), "total_gb": round(total_gb, 2)}

    def _read_process_memory_gb(self) -> float:
        # Optional process memory information; fallback to 0
        if psutil is None:
            return 0.0
        try:
            proc = psutil.Process(os.getpid())
            rss = float(proc.memory_info().rss)
            return round(rss / (1024 ** 3), 2)
        except Exception:
            return 0.0

    def _read_total_memory_gb(self) -> float:
        if psutil is None:
            return 0.0
        try:
            vm = psutil.virtual_memory()
            return round(float(vm.total) / (1024 ** 3), 2)
        except Exception:
            return 0.0

    def _maybe_log(self, snapshot: dict) -> None:
        if not self.debug_logging:
            return
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": time.time(), **snapshot}) + "\n")
        except Exception:
            # Logging should never break the main flow
            pass


_SYSTEM_MONITOR_INSTANCE: SystemMonitor | None = None


def get_system_monitor() -> SystemMonitor:
    global _SYSTEM_MONITOR_INSTANCE
    if _SYSTEM_MONITOR_INSTANCE is None:
        _SYSTEM_MONITOR_INSTANCE = SystemMonitor()
    return _SYSTEM_MONITOR_INSTANCE


