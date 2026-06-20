"""
OpenRouter embedding service via openai-compatible /embeddings endpoint.
768-dimensional embeddings for semantic food search.

NOTE: nvidia/nemotron-3.5-content-safety:free does NOT support embeddings.
      Set EMBEDDING_MODEL in .env to an embedding-capable model on OpenRouter,
      e.g. "text-embedding-3-small" (requires OpenAI key) or another provider.
      Current DB schema expects 768-dim vectors — pick a model that matches.
"""
import asyncio
import time
from typing import List
from openai import OpenAI
from app.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 768
_RATE_LIMIT_DELAY = 0.1


def _client() -> OpenAI:
    return OpenAI(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )


def embed_text_sync(text: str, task_type: str = "retrieval_document") -> List[float]:
    """Synchronous embedding — used by the import script."""
    result = _client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return result.data[0].embedding


async def embed_text(text: str, task_type: str = "retrieval_document") -> List[float]:
    """Async wrapper — used by API routes at inference time."""
    loop = asyncio.get_event_loop()
    vec = await loop.run_in_executor(None, lambda: embed_text_sync(text, task_type))
    return vec


async def embed_query(text: str) -> List[float]:
    """Embed a user query."""
    return await embed_text(text, task_type="retrieval_query")


def batch_embed_sync(texts: List[str], task_type: str = "retrieval_document",
                     delay: float = _RATE_LIMIT_DELAY) -> List[List[float]]:
    """
    Batch synchronous embedding with rate-limit backoff.
    Used exclusively by the import script.
    """
    vectors = []
    for i, text in enumerate(texts):
        try:
            vec = embed_text_sync(text, task_type)
            vectors.append(vec)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = min(60, delay * (2 ** (i % 5)))
                print(f"  Rate limit hit, waiting {wait:.1f}s…")
                time.sleep(wait)
                vec = embed_text_sync(text, task_type)
                vectors.append(vec)
            else:
                print(f"  Embed failed for text '{text[:40]}': {e}")
                vectors.append([0.0] * EMBEDDING_DIM)
        time.sleep(delay)
    return vectors
