from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional, Tuple

from sqlmodel import Session, select
import asyncio

from app.models.session import SessionModel, MessageModel
from app.models.settings import KnowledgeEntryModel
from app.services.summarization import SummarizationService


class ContextManager:
    """Handles context trimming, summarization, and knowledge capture for long chats.

    Minimal implementation to satisfy Task 013 acceptance and tests:
    - Trigger on >40 messages.
    - Summarize older messages by extracting simple fact-like lines ("key: value").
    - Persist knowledge entries to a dedicated table.
    - Mark older messages as trimmed and allow restoring a subset.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def should_trim(self, message_count: int) -> bool:
        return message_count > 40

    def _iter_messages(self, session_id: str) -> List[MessageModel]:
        return self._db.exec(
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at)
        ).all()

    def extract_facts(self, texts: Iterable[Tuple[int, str]]) -> List[Tuple[str, str, Optional[int]]]:
        """Extract simple key: value facts.

        texts: iterable of (source_message_id, text)
        returns: list of (key, value, source_message_id)
        """
        out: List[Tuple[str, str, Optional[int]]] = []
        for mid, t in texts:
            if not t:
                continue
            # Take first 'key: value' pair in the line
            parts = t.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if key and value:
                    out.append((key, value, mid))
        return out

    def upsert_knowledge(self, session_id: str, facts: List[Tuple[str, str, Optional[int]]]) -> None:
        for key, value, mid in facts:
            row = KnowledgeEntryModel(
                session_id=session_id,
                key=key,
                value=value,
                source_message_id=mid,
                created_at=datetime.utcnow(),
            )
            self._db.add(row)
        if facts:
            self._db.commit()

    async def summarize_and_trim_async(self, session_id: str, keep_last_n: int = 10, max_tokens: int = 400) -> str:
        """Create a brief summary of older messages and mark them as trimmed.

        Returns the summary text stored with the session.
        """
        msgs = self._iter_messages(session_id)
        if len(msgs) <= keep_last_n:
            return ""
        older = msgs[:-keep_last_n]
        # Extract facts for knowledge capture
        facts = self.extract_facts([(m.id or 0, m.content) for m in older])
        self.upsert_knowledge(session_id, facts)

        # Prepare text to summarize using local LLM if configured
        older_text = "\n".join(m.content for m in older)
        summarizer = SummarizationService()
        summary_text = await summarizer.summarize(older_text, max_tokens=max_tokens)
        if not summary_text:
            # Fallback to crude summary based on facts
            summary_lines: List[str] = []
            seen_keys: set[str] = set()
            for k, v, _mid in facts:
                lk = k.lower()
                if lk in seen_keys:
                    continue
                seen_keys.add(lk)
                summary_lines.append(f"{k}: {v}")
                if len(summary_lines) >= 5:
                    break
            if not summary_lines:
                for m in older[:5]:
                    summary_lines.append(m.content[:200])
            summary_text = "\n".join(summary_lines).strip()

        # Persist summary in the session metadata
        session = self._db.get(SessionModel, session_id)
        if session:
            meta = dict(session.metadata_json or {})
            meta["last_summary"] = summary_text
            session.metadata_json = meta
            self._db.add(session)
            self._db.commit()

        # Mark trimmed messages
        for m in older:
            if not m.is_trimmed:
                m.is_trimmed = True
                self._db.add(m)
        self._db.commit()
        return summary_text

    def summarize_and_trim(self, session_id: str, keep_last_n: int = 10, max_tokens: int = 400) -> str:
        """Sync wrapper for contexts that aren't async-aware.

        Used from the SSE generator which is async; we can run the async summarizer directly.
        """
        # In our usage from FastAPI SSE coroutine, we can safely run the async call via asyncio.run if no loop
        try:
            return asyncio.run(self.summarize_and_trim_async(session_id, keep_last_n=keep_last_n, max_tokens=max_tokens))
        except RuntimeError:
            # If a loop exists already (unlikely in our test path), create a task and wait
            coro = self.summarize_and_trim_async(session_id, keep_last_n=keep_last_n, max_tokens=max_tokens)
            return asyncio.get_event_loop().run_until_complete(coro)

    def get_last_summary(self, session_id: str) -> str:
        session = self._db.get(SessionModel, session_id)
        if not session or not session.metadata_json:
            return ""
        return str(session.metadata_json.get("last_summary") or "")

    def list_knowledge(self, session_id: str, limit: int = 5) -> List[KnowledgeEntryModel]:
        rows = self._db.exec(
            select(KnowledgeEntryModel)
            .where(KnowledgeEntryModel.session_id == session_id)
            .order_by(KnowledgeEntryModel.id.desc())
            .limit(limit)
        ).all()
        return rows

    def restore_trimmed(self, session_id: str, count: int) -> int:
        if count <= 0:
            return 0
        trimmed = self._db.exec(
            select(MessageModel)
            .where(MessageModel.session_id == session_id, MessageModel.is_trimmed == True)  # noqa: E712
            .order_by(MessageModel.created_at.desc())
            .limit(count)
        ).all()
        restored = 0
        for m in trimmed:
            if m.is_trimmed:
                m.is_trimmed = False
                self._db.add(m)
                restored += 1
        if restored:
            self._db.commit()
        return restored


