from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import httpx  # type: ignore
except Exception:  # pragma: no cover
    httpx = None  # type: ignore


@dataclass
class _Result:
    title: str
    url: str
    snippet: str


class _DefaultHTTPClient:
    async def get_json(self, url: str, params: dict | None = None, headers: dict | None = None) -> dict:
        if httpx is None:
            return {}
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r.json()


class SearchService:
    """Performs web searches with rate limiting and short-term caching.

    Primary engine: DuckDuckGo Instant Answer API (no key).
    Optional fallback: Bing Web Search when API key provided.
    """

    def __init__(
        self,
        *,
        rate_limit_per_min: int = 13,
        cache_ttl_seconds: int = 120,
        debug_log_path: Optional[Path] = Path("data/logs/search_debug.log"),
        http_client: Optional[object] = None,
        bing_api_key: Optional[str] = None,
    ) -> None:
        self.rate_limit_per_min = rate_limit_per_min
        self.cache_ttl_seconds = cache_ttl_seconds
        self.debug_log_path = Path(debug_log_path) if debug_log_path else None
        self._http = http_client or _DefaultHTTPClient()
        self._bing_api_key = bing_api_key
        # query -> (timestamp, results)
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        self._recent_timestamps: list[float] = []

    def _allow_request(self) -> bool:
        now = time.time()
        window_start = now - 60.0
        # drop old
        self._recent_timestamps = [t for t in self._recent_timestamps if t >= window_start]
        if len(self._recent_timestamps) >= self.rate_limit_per_min:
            return False
        self._recent_timestamps.append(now)
        return True

    async def search(self, query: str) -> list[dict]:
        if not query:
            return []
        # Cache
        now = time.time()
        cached = self._cache.get(query)
        if cached and (now - cached[0]) <= self.cache_ttl_seconds:
            return cached[1]

        if not self._allow_request():
            return []

        results: list[dict] = []

        # Try DuckDuckGo first
        try:
            ddg = await self._http.get_json(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            )
            results = self._parse_duckduckgo(ddg)
        except Exception:
            results = []

        # Fallback to Bing if no results and key is present
        if not results and self._bing_api_key:
            try:
                bing = await self._http.get_json(
                    "https://api.bing.microsoft.com/v7.0/search",
                    params={"q": query, "mkt": "en-US", "safeSearch": "Moderate"},
                    headers={"Ocp-Apim-Subscription-Key": self._bing_api_key},
                )
                results = self._parse_bing(bing)
            except Exception:
                results = []

        self._cache[query] = (now, results)
        self._maybe_log({"query": query, "results": results})
        return results

    def _parse_duckduckgo(self, data: dict) -> list[dict]:
        out: list[dict] = []
        if not isinstance(data, dict):
            return out
        abstract = (data.get("AbstractText") or "").strip()
        if abstract:
            out.append({"title": "DuckDuckGo", "url": "", "snippet": abstract})
        related = data.get("RelatedTopics") or []
        if isinstance(related, list):
            for item in related:
                if isinstance(item, dict):
                    txt = (item.get("Text") or "").strip()
                    url = (item.get("FirstURL") or "").strip()
                    if txt:
                        out.append({"title": txt.split(" - ")[0] if " - " in txt else txt, "url": url, "snippet": txt})
        return out[:10]

    def _parse_bing(self, data: dict) -> list[dict]:
        out: list[dict] = []
        if not isinstance(data, dict):
            return out
        web = data.get("webPages", {}).get("value", []) if isinstance(data.get("webPages"), dict) else []
        for item in web:
            try:
                out.append({
                    "title": str(item.get("name") or ""),
                    "url": str(item.get("url") or ""),
                    "snippet": str(item.get("snippet") or ""),
                })
            except Exception:
                continue
        return out[:10]

    def _maybe_log(self, obj: dict) -> None:
        if not self.debug_log_path:
            return
        try:
            self.debug_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.debug_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": time.time(), **obj}) + "\n")
        except Exception:
            pass


# Singleton accessor for integration points
_SEARCH_SERVICE_INSTANCE: SearchService | None = None


def get_search_service(debug_enabled: bool = False, bing_api_key: Optional[str] = None) -> SearchService:
    global _SEARCH_SERVICE_INSTANCE
    if _SEARCH_SERVICE_INSTANCE is None:
        log_path = Path("data/logs/search_debug.log") if debug_enabled else None
        _SEARCH_SERVICE_INSTANCE = SearchService(debug_log_path=log_path, bing_api_key=bing_api_key)
    else:
        # Update debug path if toggled at runtime
        _SEARCH_SERVICE_INSTANCE.debug_log_path = Path("data/logs/search_debug.log") if debug_enabled else None
        _SEARCH_SERVICE_INSTANCE._bing_api_key = bing_api_key
    return _SEARCH_SERVICE_INSTANCE


