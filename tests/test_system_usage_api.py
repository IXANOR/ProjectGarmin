import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_system_usage_endpoint_structure(monkeypatch):
    # Force fresh readings by resetting any cached state if present
    try:
        import importlib
        sm = importlib.import_module("app.services.system_monitor")
        # Reset singleton (if created) to ensure deterministic behavior
        if hasattr(sm, "_SYSTEM_MONITOR_INSTANCE"):
            sm._SYSTEM_MONITOR_INSTANCE = None  # type: ignore[attr-defined]
    except Exception:
        pass

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/system/usage")
        assert resp.status_code == 200
        data = resp.json()
        # Expected top-level keys
        assert set(data.keys()) == {"cpu", "memory", "gpu"}
        # CPU
        assert set(data["cpu"].keys()) == {"percent", "used_gb", "total_gb"}
        assert isinstance(data["cpu"]["percent"], (int, float))
        # Memory
        assert set(data["memory"].keys()) == {"percent", "used_gb", "total_gb"}
        assert data["memory"]["total_gb"] >= data["memory"]["used_gb"]
        # GPU structure present even if zeros on systems without NVML
        assert set(data["gpu"].keys()) == {"percent", "used_gb", "total_gb"}


@pytest.mark.asyncio
async def test_system_settings_toggle_debug_logging_and_mode(monkeypatch):
    # Intercept logging side-effect to avoid filesystem writes
    import importlib
    sm = importlib.import_module("app.services.system_monitor")

    counter = {"n": 0}

    def _fake_log(self, snapshot):  # type: ignore[no-redef]
        counter["n"] += 1

    # Replace logger with counter
    monkeypatch.setattr(sm.SystemMonitor, "_maybe_log", _fake_log, raising=True)

    # Reset singleton to ensure patched method is used
    if hasattr(sm, "_SYSTEM_MONITOR_INSTANCE"):
        sm._SYSTEM_MONITOR_INSTANCE = None  # type: ignore[attr-defined]

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Defaults
        get0 = await client.get("/api/system/settings")
        assert get0.status_code == 200
        s0 = get0.json()
        assert set(s0.keys()) == {"mode", "debug_logging"}
        assert s0["mode"] in {"minimal", "expanded"}
        assert s0["debug_logging"] is False

        # Enable debug logging and set expanded mode
        upd = await client.post("/api/system/settings", json={"debug_logging": True, "mode": "expanded"})
        assert upd.status_code == 200
        s1 = upd.json()
        assert s1["debug_logging"] is True
        assert s1["mode"] == "expanded"

        # Calling /usage should trigger a log attempt (count increases)
        counter["n"] = 0
        u1 = await client.get("/api/system/usage")
        assert u1.status_code == 200
        assert counter["n"] >= 1

        # Disable debug logging; subsequent usage fetch should not log
        upd2 = await client.post("/api/system/settings", json={"debug_logging": False})
        assert upd2.status_code == 200
        counter["n"] = 0
        u2 = await client.get("/api/system/usage")
        assert u2.status_code == 200
        assert counter["n"] == 0


