from __future__ import annotations

import hashlib
import math

LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-002"
EMBEDDING_PROVIDER_ENV = "EMBEDDING_PROVIDER"


class MockEmbedder:
    """Deterministic embedding backend used by tests and default classroom runs."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self._backend_name = "mock embeddings fallback"

    def __call__(self, text: str) -> list[float]:
        digest = hashlib.md5(text.encode()).hexdigest()
        seed = int(digest, 16)
        vector = []
        for _ in range(self.dim):
            seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
            vector.append((seed / 0xFFFFFFFF) * 2 - 1)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class LocalEmbedder:
    """Sentence Transformers-backed local embedder."""

    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._backend_name = model_name
        self.model = SentenceTransformer(model_name)

    def __call__(self, text: str) -> list[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return [float(value) for value in embedding]


class OpenAIEmbedder:
    """OpenAI embeddings API-backed embedder."""

    def __init__(self, model_name: str = OPENAI_EMBEDDING_MODEL) -> None:
        from openai import OpenAI

        self.model_name = model_name
        self._backend_name = model_name
        self.client = OpenAI()

    def __call__(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model_name, input=text)
        return [float(value) for value in response.data[0].embedding]


class GeminiEmbedder:
    """Gemini API-backed embedder using Google's genai SDK."""

    def __init__(
        self,
        model_name: str = GEMINI_EMBEDDING_MODEL,
        output_dimensionality: int | None = None,
    ) -> None:
        from google import genai

        self.model_name = model_name
        self.output_dimensionality = output_dimensionality
        self._backend_name = (
            model_name
            if output_dimensionality is None
            else f"{model_name}:{output_dimensionality}"
        )
        self.client = genai.Client()

    def __call__(self, text: str) -> list[float]:
        kwargs = {
            "model": self.model_name,
            "contents": text,
        }
        if self.output_dimensionality is not None:
            from google.genai import types

            kwargs["config"] = types.EmbedContentConfig(
                output_dimensionality=self.output_dimensionality
            )

        response = self.client.models.embed_content(**kwargs)
        embeddings = getattr(response, "embeddings", None)
        if embeddings:
            values = getattr(embeddings[0], "values", embeddings[0])
            return [float(value) for value in values]

        embedding = getattr(response, "embedding", None)
        if embedding is not None:
            values = getattr(embedding, "values", embedding)
            return [float(value) for value in values]

        raise ValueError("Gemini embedding response did not contain embeddings")


_mock_embed = MockEmbedder()
