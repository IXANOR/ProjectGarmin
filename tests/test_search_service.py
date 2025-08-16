import asyncio
import json
from pathlib import Path

import pytest

from app.services.search_service import SearchService


class DummyHTTPClient:
    def __init__(self, responses: dict[str, dict]):
        self.responses = responses
        self.calls: list[str] = []

    async def get_json(self, url: str, params: dict | None = None, headers: dict | None = None) -> dict:
        key = json.dumps({"url": url, "params": params or {}, "headers": headers or {}}, sort_keys=True)
        self.calls.append(key)
        return self.responses.get(key, {})


@pytest.mark.asyncio
async def test_duckduckgo_search_basic_and_cache(tmp_path: Path):
    # Prepare a fake response for DuckDuckGo Instant Answer API
    query = "what is the capital of france"
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
    key = json.dumps({"url": url, "params": params, "headers": {}}, sort_keys=True)
    dummy = DummyHTTPClient({
        key: {
            "AbstractText": "Paris is the capital and most populous city of France.",
            "RelatedTopics": [
                {"Text": "Paris - Capital of France", "FirstURL": "https://duckduckgo.com/Paris"}
            ],
        }
    })

    svc = SearchService(rate_limit_per_min=13, debug_log_path=tmp_path / "search_debug.log", http_client=dummy)
    results1 = await svc.search(query)
    assert any("paris" in r.get("snippet", "").lower() for r in results1)
    # Second call within 2 minutes should hit cache: no extra http calls recorded
    _ = await svc.search(query)
    # Only one call should be made as the second is cached
    assert len(dummy.calls) == 1


@pytest.mark.asyncio
async def test_rate_limiting_prevents_excess():
    svc = SearchService(rate_limit_per_min=2, debug_log_path=None, http_client=None)

    # Monkeypatch internal clock to simulate fast calls
    svc._recent_timestamps.clear()
    # First two are allowed
    assert svc._allow_request() is True
    assert svc._allow_request() is True
    # Third within the same minute should be blocked
    assert svc._allow_request() is False


@pytest.mark.asyncio
async def test_debug_logging_enabled(tmp_path: Path):
    query = "test log"
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
    key = json.dumps({"url": url, "params": params, "headers": {}}, sort_keys=True)
    dummy = DummyHTTPClient({ key: {"AbstractText": "", "RelatedTopics": []} })
    log_path = tmp_path / "search_debug.log"

    svc = SearchService(rate_limit_per_min=13, debug_log_path=log_path, http_client=dummy)
    await svc.search(query)
    # Log file should exist and contain at least one JSON line with the query
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert any("test log" in line for line in content)


