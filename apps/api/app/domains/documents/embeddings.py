import math
from dataclasses import dataclass

from openai import OpenAI, OpenAIError

from apps.api.app.core.config import get_settings


class EmbeddingUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: list[list[float]]
    model: str
    tokens_used: int


def embed_texts(texts: list[str]) -> EmbeddingBatch:
    settings = get_settings()
    if not settings.openai_api_key:
        raise EmbeddingUnavailable("OPENAI_API_KEY is not configured.")
    if not texts:
        raise ValueError("At least one text chunk is required.")

    client = OpenAI(api_key=settings.openai_api_key, timeout=30.0, max_retries=2)
    try:
        result = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
            dimensions=settings.openai_embedding_dimensions,
            encoding_format="float",
        )
    except OpenAIError as exc:
        raise EmbeddingUnavailable("The embedding provider request failed.") from exc

    vectors = [item.embedding for item in sorted(result.data, key=lambda item: item.index)]
    if len(vectors) != len(texts) or any(
        len(vector) != settings.openai_embedding_dimensions
        or any(not math.isfinite(value) for value in vector)
        for vector in vectors
    ):
        raise EmbeddingUnavailable("The embedding provider returned an invalid vector shape.")
    return EmbeddingBatch(
        vectors=vectors,
        model=result.model,
        tokens_used=result.usage.total_tokens,
    )
