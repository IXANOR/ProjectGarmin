from __future__ import annotations

import os
from typing import Optional


class SummarizationService:
    """Summarize long text using a local LLM when available, otherwise fall back.

    Providers (opt-in via env):
    - OLLAMA: set LLM_SUMMARIZER_PROVIDER=OLLAMA and LLM_SUMMARIZER_MODEL (e.g., 'mistral')
      Calls http://127.0.0.1:11434/api/generate
    - LMSTUDIO: set LLM_SUMMARIZER_PROVIDER=LMSTUDIO and LLM_SUMMARIZER_URL, LLM_SUMMARIZER_MODEL
      Calls OpenAI-compatible endpoint at URL

    Default: fast heuristic fallback (first N sentences/lines).
    """

    def __init__(self, provider: Optional[str] = None) -> None:
        self._provider = (provider or os.getenv("LLM_SUMMARIZER_PROVIDER") or "").upper()
        self._model = os.getenv("LLM_SUMMARIZER_MODEL") or ""
        self._url = os.getenv("LLM_SUMMARIZER_URL") or ""

    async def summarize(self, text: str, max_tokens: int = 400) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        try:
            if self._provider == "OLLAMA":
                return await self._summarize_ollama(text, max_tokens)
            if self._provider == "LMSTUDIO":
                return await self._summarize_lmstudio(text, max_tokens)
        except Exception:
            # Fall back silently
            pass
        # Fallback: naive summarization (first sentences/lines trimmed to ~max_tokens words)
        return self._fallback(text, max_tokens=max_tokens)

    async def _summarize_ollama(self, text: str, max_tokens: int) -> str:
        import httpx

        model = self._model or "mistral"
        url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434") + "/api/generate"
        prompt = (
            "Summarize the following conversation context into concise bullet points, "
            "focusing on durable facts and key points, within "
            f"{max_tokens} tokens.\n\n" + text
        )
        payload = {"model": model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            out = data.get("response") or ""
            return out.strip()

    async def _summarize_lmstudio(self, text: str, max_tokens: int) -> str:
        import httpx

        model = self._model or "gpt-3.5-turbo"
        url = self._url or "http://127.0.0.1:1234/v1/chat/completions"
        messages = [
            {"role": "system", "content": "You are a helpful assistant summarizing chat history."},
            {
                "role": "user",
                "content": (
                    "Summarize the following conversation context into concise bullet points, "
                    "focusing on durable facts and key points, within "
                    f"{max_tokens} tokens.\n\n{text}"
                ),
            },
        ]
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                url,
                json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2},
            )
            r.raise_for_status()
            data = r.json()
            choices = data.get("choices") or []
            if choices:
                msg = choices[0].get("message") or {}
                return (msg.get("content") or "").strip()
            return ""

    def _fallback(self, text: str, max_tokens: int) -> str:
        words = text.split()
        limit = max(10, min(len(words), max_tokens))
        return " ".join(words[:limit])


