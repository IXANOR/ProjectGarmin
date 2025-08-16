# ADR-007: Conversation Memory and Context Management

## Status
Accepted

## Context
- The model context window is limited (~12k tokens) and cannot be increased by configuration alone.
- We need long-running conversations without exceeding the model max tokens.
- We already have ChromaDB for retrieval and per-session scoping via metadata.

## Decision
Use a layered memory approach that keeps most information outside the prompt and injects only concise, relevant pieces at inference time.

1) External conversation memory (ChromaDB)
- Persist per-session memory artifacts in ChromaDB with metadata: `session_id`, `memory_type`.
- Memory types:
  - `summary`: rolling compressed summary of earlier turns
  - `facts`: durable, structured fact/task bullets
  - `tools`: compact snippets from tools (e.g., web search mini-summaries)
- On each user turn, retrieve only the top 2–3 concise items to inject.

2) Rolling summarization
- After N messages or when tail tokens exceed a threshold, create a short summary of prior turns and store it as a `summary` artifact.
- Keep only recent M messages verbatim; include the rolling summary plus retrieved `facts`/`tools`.

3) Retrieval strategy and budgets
- Chunk documents small (≈200–300 tokens) with overlap (≈30–60).
- Per turn:
  - Query `summary`, `facts`, `tools` within the session scope; `top_k` 3–5.
  - Optionally re-rank top 20 and keep best 3.
  - Apply a strict token budget for memory + tools (e.g., ≤800 tokens total).
- Keep RAG chunks small (`top_k` 3–5) and fit under a total per-turn budget.

4) Web search (when enabled)
- Only include 2–3 short excerpts on recency cues; convert into `tools` artifacts with timestamp/source.

5) Tuning knobs (env/config)
- `EMBEDDINGS_DEVICE=cpu`
- `RAG_CHUNK_SIZE=300`
- `RAG_CHUNK_OVERLAP=50`
- `RAG_TOP_K_MAX=5`
- `RAG_SIMILARITY_THRESHOLD=0.25`
- `RAG_RE_RANK_TOP_N=20` (optional)
- `RAG_FINAL_TOP_K=3`
- `RAG_PER_TURN_MEMORY_BUDGET_TOKENS=800`
- `CONVO_SUMMARY_EVERY_N_MESSAGES=12`
- `CONVO_SUMMARY_MAX_TOKENS=400`

6) Prompt structure (high level)
- Brief system instructions
- Recent conversation tail (last K messages)
- Rolling summary (≤ `CONVO_SUMMARY_MAX_TOKENS`)
- Retrieved `facts` (2–3 bullets) and `tools` (2 short snippets)
- Retrieved RAG chunks (≤ `RAG_FINAL_TOP_K`)

7) Observability
- Keep `: RAG_DEBUG` and `: SEARCH_DEBUG` SSE lines.
- Add `: MEMORY_DEBUG` to show what memory artifacts were injected.

## Consequences
- Pros: Extends practical context, reduces prompt size, reuses ChromaDB infra.
- Cons: Summaries may lose nuance; requires ranking, triggers, and budgets.

## Implementation notes
- Store artifacts in the existing `documents` collection with metadata like:
  - `{ "session_id": <sid>, "memory_type": "summary"|"facts"|"tools", "chunk_index": 0 }`
- Use the existing embedder and query paths; unify persistence.
- Add a helper in the chat pipeline to (a) enforce budgets, (b) fetch memory artifacts, (c) assemble prompt sections.

## Testing (TDD)
- After N messages, a `summary` artifact is created and older turns compress.
- Retrieved `facts` are injected under the per-turn memory budget.
- Total tokens for memory+tools ≤ `RAG_PER_TURN_MEMORY_BUDGET_TOKENS`.
- Tightening `RAG_FINAL_TOP_K` reduces prompt tokens predictably.

## References
- ADR-005 (RAG Architecture)
- ADR-001 (Backend Architecture)
