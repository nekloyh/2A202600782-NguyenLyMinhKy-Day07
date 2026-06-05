from __future__ import annotations

import uuid
from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.

    Each Document is stored as a single record (the store does not chunk —
    chunking is a separate concern handled by the chunker classes). The
    document id is preserved under metadata['doc_id'] so delete_document and
    metadata filtering work identically in both backends.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            self._client = chromadb.EphemeralClient()
            # A unique collection name keeps each store instance isolated, even
            # when several stores share the same logical collection_name.
            self._collection = self._client.get_or_create_collection(
                name=f"{collection_name}-{uuid.uuid4().hex[:8]}",
                metadata={"hnsw:space": "cosine"},
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    # ------------------------------------------------------------------ #
    # Helpers (in-memory backend)
    # ------------------------------------------------------------------ #
    def _make_record(self, doc: Document) -> dict[str, Any]:
        record_id = str(self._next_index)
        self._next_index += 1
        return {
            "id": record_id,
            "doc_id": doc.id,
            "content": doc.content,
            "metadata": {**doc.metadata, "doc_id": doc.id},
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        query_embedding = self._embedding_fn(query)
        scored = [
            {
                "content": record["content"],
                "metadata": record["metadata"],
                "score": _dot(query_embedding, record["embedding"]),
            }
            for record in records
        ]
        scored.sort(key=lambda result: result["score"], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _build_where(metadata_filter: dict) -> dict:
        """Translate a flat metadata filter into ChromaDB `where` syntax."""
        if len(metadata_filter) == 1:
            return dict(metadata_filter)
        return {"$and": [{key: value} for key, value in metadata_filter.items()]}

    def _chroma_results(self, response: dict) -> list[dict[str, Any]]:
        documents = (response.get("documents") or [[]])[0]
        metadatas = (response.get("metadatas") or [[]])[0]
        distances = (response.get("distances") or [[]])[0]
        results = []
        for content, metadata, distance in zip(documents, metadatas, distances):
            # ChromaDB cosine *distance* = 1 - cosine similarity.
            results.append(
                {
                    "content": content,
                    "metadata": metadata or {},
                    "score": 1.0 - distance,
                }
            )
        return results

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        if self._use_chroma:
            ids, documents, embeddings, metadatas = [], [], [], []
            for doc in docs:
                ids.append(str(self._next_index))
                self._next_index += 1
                documents.append(doc.content)
                embeddings.append(self._embedding_fn(doc.content))
                metadatas.append({**doc.metadata, "doc_id": doc.id})
            self._collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        else:
            for doc in docs:
                self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma:
            count = self._collection.count()
            if count == 0:
                return []
            response = self._collection.query(
                query_embeddings=[self._embedding_fn(query)],
                n_results=min(top_k, count),
            )
            return self._chroma_results(response)

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(
        self, query: str, top_k: int = 3, metadata_filter: dict = None
    ) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma:
            count = self._collection.count()
            if count == 0:
                return []
            query_kwargs: dict[str, Any] = {
                "query_embeddings": [self._embedding_fn(query)],
                "n_results": min(top_k, count),
            }
            if metadata_filter:
                query_kwargs["where"] = self._build_where(metadata_filter)
            response = self._collection.query(**query_kwargs)
            return self._chroma_results(response)

        if metadata_filter:
            records = [
                record
                for record in self._store
                if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
            ]
        else:
            records = self._store
        return self._search_records(query, records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma:
            before = self._collection.count()
            self._collection.delete(where={"doc_id": doc_id})
            return self._collection.count() < before

        before = len(self._store)
        self._store = [
            record for record in self._store if record["metadata"].get("doc_id") != doc_id
        ]
        return len(self._store) < before
