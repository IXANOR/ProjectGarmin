from typing import AsyncGenerator, List
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from sqlmodel import Session, select

from app.core.db import get_session
from app.models.session import SessionModel, MessageModel
from app.models.settings import SearchSettingsModel
from app.models.file import FileModel
from app.services.rag import RagService
from app.services.search_service import get_search_service
from app.core.config import get_rag_token_budget, get_default_enabled_sources


router = APIRouter()

# Simple in-memory cache: (session_id, question) -> (timestamp, results)
_RAG_CACHE: dict[tuple[str, str], tuple[float, list[dict]]] = {}


@router.post("/chat")
async def chat_endpoint(payload: dict, db: Session = Depends(get_session)) -> StreamingResponse:
    session_id = payload.get("session_id")
    messages: List[dict] | None = payload.get("messages")
    if not session_id or not isinstance(messages, list) or not messages:
        raise HTTPException(status_code=400, detail="Invalid request body")

    # Ensure session exists
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Persist incoming user messages
    for msg in messages:
        db.add(MessageModel(session_id=session_id, role=msg.get("role", "user"), content=msg.get("content", "")))
    # Persist assistant reply (mock)
    assistant_full = "Hello from mock AI!"
    db.add(MessageModel(session_id=session_id, role="assistant", content=assistant_full))
    db.commit()

    # RAG retrieval debug payload (Task 005 + Task 008)
    rag_debug_mode = (os.getenv("RAG_DEBUG_MODE") or "true").lower() not in {"0", "false", "no"}
    user_contents = [m.get("content", "") for m in messages if m.get("role", "user") == "user"]
    last_user = user_contents[-1] if user_contents else ""
    rag_top_k_max = int(os.getenv("RAG_TOP_K_MAX") or "40")
    rag_token_budget = get_rag_token_budget()
    sim_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD") or "0.25")
    cache_ttl_seconds = int(os.getenv("RAG_CACHE_TTL_SECONDS") or "300")
    rag_timeout_seconds = float(os.getenv("RAG_TIMEOUT_SECONDS") or "6")

    # Task 008: supported/allowed sources; default to all
    DEFAULT_SOURCES = get_default_enabled_sources()
    sources = payload.get("sources")
    if isinstance(sources, list) and all(isinstance(s, str) for s in sources):
        allowed_sources = [s.lower() for s in sources if s]
        # Only keep known ones; ignore unknown values silently
        allowed_sources = [s for s in allowed_sources if s in DEFAULT_SOURCES]
        if not allowed_sources:
            allowed_sources = DEFAULT_SOURCES
    else:
        allowed_sources = DEFAULT_SOURCES

    should_skip_rag = len(last_user) < 10

    rag_debug_payload: dict = {"used": False, "citations": [], "chunks": [], "per_source": {"pdf": [], "image": [], "audio": []}}
    if rag_debug_mode:
        if not should_skip_rag:
            # Try cache first
            cache_key = (session_id, last_user, tuple(allowed_sources))
            now = time.time()
            cached = _RAG_CACHE.get(cache_key)
            if cached and now - cached[0] <= cache_ttl_seconds:
                results = cached[1]
            else:
                rag = RagService()
                def _q_session() -> list[dict]:
                    # Query within session scope (no source filter here; we'll split/filter later)
                    return rag.query(last_user, top_k=rag_top_k_max, where={"session_id": session_id})
                def _q_global(n: int) -> list[dict]:
                    # Query within global scope
                    return rag.query(last_user, top_k=n, where={"session_id": "GLOBAL"})

                results_session: list[dict] = []
                results_global: list[dict] = []
                try:
                    with ThreadPoolExecutor(max_workers=2) as ex:
                        fut_sess = ex.submit(_q_session)
                        try:
                            results_session = fut_sess.result(timeout=rag_timeout_seconds)
                        except FuturesTimeout:
                            results_session = []
                        except Exception:
                            results_session = []
                        remaining = max(0, rag_top_k_max - len(results_session))
                        if remaining > 0:
                            fut_glob = ex.submit(_q_global, remaining)
                            try:
                                results_global = fut_glob.result(timeout=max(0.0, rag_timeout_seconds - 0.01))
                            except FuturesTimeout:
                                results_global = []
                            except Exception:
                                results_global = []
                except Exception:
                    results_session, results_global = [], []
                # Merge session+global first
                results = results_session + results_global
                _RAG_CACHE[cache_key] = (now, results)

            file_ids = {r.get("metadata", {}).get("file_id") for r in results if r.get("metadata")}
            id_to_name: dict[str, str] = {}
            soft_deleted_ids: set[str] = set()
            if file_ids:
                rows = db.exec(select(FileModel).where(FileModel.id.in_(list(file_ids)))).all()
                id_to_name = {row.id: row.name for row in rows}
                soft_deleted_ids = {row.id for row in rows if getattr(row, "is_soft_deleted", False)}

            # Split by source_type for Task 008; default missing to "pdf"
            def _infer_source(meta: dict | None) -> str:
                if not meta:
                    return "pdf"
                st = meta.get("source_type")
                return (st or "pdf").lower()

            # Exclude soft-deleted files from RAG context
            if soft_deleted_ids:
                results = [r for r in results if r.get("metadata", {}).get("file_id") not in soft_deleted_ids]
            # Apply threshold first
            filtered = [r for r in results if (r.get("score") is None or r.get("score") >= sim_threshold)]
            per_source: dict[str, list[dict]] = {"pdf": [], "image": [], "audio": []}
            for r in filtered:
                src = _infer_source(r.get("metadata"))
                if src not in per_source:
                    # Ignore unknown source types in debug
                    continue
                per_source[src].append(r)

            # Sort each source list by score desc (None last)
            def _score_key(item: dict) -> float:
                s = item.get("score")
                return s if isinstance(s, (int, float)) else -1.0

            for k in per_source.keys():
                per_source[k].sort(key=_score_key, reverse=True)

            # Apply source filter: only keep allowed in both per_source and overall selection pool
            filtered_allowed: list[dict] = []
            debug_per_source: dict[str, list[dict]] = {"pdf": [], "image": [], "audio": []}
            for k, vals in per_source.items():
                if k in allowed_sources:
                    debug_per_source[k] = [
                        {"id": v.get("id"), "metadata": v.get("metadata", {}), "score": v.get("score")}
                        for v in vals
                    ]
                    filtered_allowed.extend(vals)
                else:
                    debug_per_source[k] = []

            # Build overall selection sorted by score
            filtered_allowed.sort(key=_score_key, reverse=True)
            if should_skip_rag and not filtered:
                rag_debug_payload = {"used": False, "citations": [], "chunks": [], "per_source": debug_per_source}
            else:
                # Truncate by approximate token budget: assume ~500 tokens per chunk as default
                approx_tokens_per_chunk = 350
                max_chunks_by_budget = max(1, rag_token_budget // approx_tokens_per_chunk)
                selected = filtered_allowed[: min(len(filtered_allowed), max_chunks_by_budget, rag_top_k_max)]

                citations: list[str] = []
                chunks_debug: list[dict] = []
                for r in selected:
                    meta = r.get("metadata", {})
                    fid = meta.get("file_id")
                    idx = meta.get("chunk_index")
                    fname = id_to_name.get(fid, fid or "unknown.pdf")
                    if isinstance(idx, int):
                        citations.append(f"{fname}#{idx}")
                    else:
                        citations.append(f"{fname}#0")
                    chunks_debug.append({
                        "id": r.get("id"),
                        "metadata": meta,
                        "score": r.get("score"),
                    })

                rag_debug_payload = {"used": bool(selected), "citations": citations, "chunks": chunks_debug, "per_source": debug_per_source}

    async def event_stream() -> AsyncGenerator[bytes, None]:
        if rag_debug_mode:
            yield f": RAG_DEBUG {json.dumps(rag_debug_payload)}\n\n".encode()

        # Task 012: Internet search integration (debug-only comment lines)
        try:
            # Load search settings
            srow = db.get(SearchSettingsModel, 1)
            allow_search = bool(getattr(srow, "allow_internet_search", False)) if srow else False
            debug_search = bool(getattr(srow, "debug_logging", False)) if srow else False
            bing_key = getattr(srow, "bing_api_key", None) if srow else None
        except Exception:
            allow_search = False
            debug_search = False
            bing_key = None

        search_debug_payload = None
        if allow_search and last_user and any(k in last_user.lower() for k in ("latest", "news", "update", "recent")):
            try:
                search = get_search_service(debug_enabled=debug_search, bing_api_key=bing_key)
                # Perform async search
                results = await search.search(last_user)
                search_debug_payload = {"query": last_user, "results": results[:3]}
            except Exception:
                search_debug_payload = {"query": last_user, "results": []}

        if search_debug_payload is not None:
            yield f": SEARCH_DEBUG {json.dumps(search_debug_payload)}\n\n".encode()

        tokens = ["Hello", "from", "mock", "AI!"]
        for token in tokens:
            yield f"data: {token}\n\n".encode()
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


