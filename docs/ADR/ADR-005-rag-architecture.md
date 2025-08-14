# ADR-005: RAG Architecture

## Status
Accepted

## Context
We need to allow the AI to process PDFs, images, and audio for contextual responses. The system should work fully offline and be optimized for small-to-medium datasets.

## Decision
We will use a **local embedding model + ChromaDB** as a vector database, store references in SQLite, and retrieve relevant chunks before inference.

## Alternatives Considered
### FAISS
- **Pros:** Very fast, widely used.
- **Cons:** Less feature-rich than ChromaDB for metadata handling.

### Weaviate
- **Pros:** Many features, supports hybrid search.
- **Cons:** Requires running a separate service.

### Milvus
- **Pros:** Highly scalable.
- **Cons:** Complex setup, overkill for local app.

## Consequences
**Positive:**
- Fully offline solution.
- Easy integration with Python backend.
- Good metadata support via ChromaDB.

**Negative:**
- ChromaDB less optimized for extremely large datasets.
- Will require embedding model selection for multimodal support.
