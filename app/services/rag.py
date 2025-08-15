from __future__ import annotations

import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings
from pypdf import PdfReader


class SentenceTransformerEmbeddingModel:
    def __init__(self, model_name: str = "sentence-transformers/multi-qa-MiniLM-L12-v2", device: str = "cpu") -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name, device=device)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )
        return [v.astype(float).tolist() for v in vectors]


@dataclass
class FakeEmbeddingModel:
    embed_dim: int = 8

    def embed(self, texts: list[str]) -> list[list[float]]:
        # Deterministic pseudo-embeddings based on text hash
        vecs: list[list[float]] = []
        for t in texts:
            seed = abs(hash(t))
            vals = [((seed >> i) & 255) / 255.0 for i in range(self.embed_dim)]
            vecs.append(vals)
        return vecs


class RagService:
    def __init__(self, chroma_path: Path | str | None = None, embedder: Optional[object] = None) -> None:
        base = Path(os.getenv("CHROMA_PATH") or chroma_path or Path("data") / "chroma")
        base.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(base), settings=Settings(allow_reset=False))
        self._collection: Collection = self._client.get_or_create_collection(name="documents")
        if embedder is not None:
            self._embedder = embedder
        else:
            backend = (os.getenv("EMBEDDINGS_BACKEND") or "SENTENCE_TRANSFORMERS").upper()
            if backend == "FAKE":
                self._embedder = FakeEmbeddingModel(embed_dim=8)
            else:
                model_name = os.getenv("EMBEDDINGS_MODEL_NAME") or "sentence-transformers/multi-qa-MiniLM-L12-v2"
                device = os.getenv("EMBEDDINGS_DEVICE") or "cpu"
                self._embedder = SentenceTransformerEmbeddingModel(model_name=model_name, device=device)

    def parse_pdf(self, pdf_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(pdf_bytes))
        texts: list[str] = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts).strip()

    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        tokens = text.split()
        if chunk_size <= 0:
            return []
        if overlap >= chunk_size:
            overlap = max(0, chunk_size - 1)
        stride = max(1, chunk_size - overlap)
        chunks: list[str] = []
        for start in range(0, len(tokens), stride):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            if not chunk_tokens:
                break
            chunks.append(" ".join(chunk_tokens))
            if end >= len(tokens):
                break
        return chunks

    def persist_chunks(self, file_id: str, session_id: Optional[str], chunks: list[str]) -> None:
        if not chunks:
            return
        ids = [f"{file_id}:{i}" for i in range(len(chunks))]
        metadatas = [
            {"file_id": file_id, "session_id": (session_id if session_id is not None else "GLOBAL"), "chunk_index": i}
            for i in range(len(chunks))
        ]
        embeddings = self._embedder.embed(chunks)
        self._collection.add(ids=ids, documents=chunks, metadatas=metadatas, embeddings=embeddings)

    def query(self, text: str, top_k: int = 5, where: Optional[dict] = None) -> list[dict]:
        query_vec = self._embedder.embed([text])
        # Ask Chroma to include distances for scoring if available
        try:
            result = self._collection.query(
                query_embeddings=query_vec,
                n_results=top_k,
                where=where,
                include=["metadatas", "documents", "distances"],
            )
        except TypeError:
            # Older versions may not support include; fallback
            result = self._collection.query(query_embeddings=query_vec, n_results=top_k, where=where)
        out: list[dict] = []
        ids0 = result.get("ids", [[]])[0]
        docs0 = result.get("documents", [[]])[0]
        metas0 = result.get("metadatas", [[]])[0]
        dists0 = result.get("distances", [[]])
        dists0 = dists0[0] if dists0 else [None] * len(ids0)
        for i in range(len(ids0)):
            dist = dists0[i] if i < len(dists0) else None
            # Convert distance to a crude similarity in [0,1] if possible
            if isinstance(dist, (int, float)):
                sim = max(0.0, 1.0 - float(dist))
            else:
                sim = None
            out.append(
                {
                    "id": ids0[i],
                    "text": docs0[i],
                    "metadata": metas0[i],
                    "score": sim,
                }
            )
        return out


