"""
Food matcher: OpenRouter canonicalization → hybrid search → ranked result.

Flow:
  raw_detection  →  canonicalize()  →  hybrid_search()  →  FoodMatch
"""
from __future__ import annotations
import json
import re
from typing import List
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.search.semantic_search import hybrid_search, SemanticSearchResult

_CANON_PROMPT = """You are an expert in Indian cuisine and nutrition databases.

A food image AI detected: "{raw_name}"

Your task: map this to the single most likely canonical Indian dish name that would exist in an Indian food database.

Rules:
- Use standard English names (e.g., "Masala Dosa", "Idli", "Sambar")
- Strip brand names, modifiers like "extra crispy", "special"
- If it's a regional variant, map to the parent dish
- If confidence is very low, use "Unknown Indian Dish"

Return ONLY valid JSON, nothing else:
{{"canonical_name": "Masala Dosa", "confidence": 0.95, "reasoning": "Mysore Ghee Roast is a variant of Masala Dosa"}}"""


async def canonicalize(raw_name: str) -> dict:
    """
    Use OpenRouter to map a raw detection string to a canonical food name.
    Falls back to the raw name when the key is missing/invalid.
    """
    from app.config import settings
    if not settings.openrouter_api_key or settings.openrouter_api_key == "your-openrouter-api-key-here":
        return {"canonical_name": raw_name, "confidence": 0.5, "reasoning": "no-key-fallback"}

    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    prompt = _CANON_PROMPT.format(raw_name=raw_name)
    try:
        response = client.chat.completions.create(
            model=settings.content_safety_model,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"canonical_name": raw_name, "confidence": 0.5, "reasoning": "fallback"}


class FoodMatch:
    __slots__ = ("canonical_name", "canonicalization_confidence",
                 "search_results", "best")

    def __init__(
        self,
        canonical_name: str,
        canonicalization_confidence: float,
        search_results: List[SemanticSearchResult],
    ):
        self.canonical_name = canonical_name
        self.canonicalization_confidence = canonicalization_confidence
        self.search_results = search_results
        self.best = search_results[0] if search_results else None

    def to_dict(self) -> dict:
        return {
            "canonical_name": self.canonical_name,
            "canonicalization_confidence": self.canonicalization_confidence,
            "matches": [r.to_dict() for r in self.search_results],
            "top_food_id": self.best.food.id if self.best else None,
            "top_score": self.best.score if self.best else 0.0,
        }


async def match_food(raw_detection: str, db: AsyncSession) -> FoodMatch:
    """
    Full pipeline: canonicalize → hybrid search → FoodMatch.
    """
    canon = await canonicalize(raw_detection)
    canonical_name = canon.get("canonical_name", raw_detection)
    canon_conf = float(canon.get("confidence", 0.5))

    results = await hybrid_search(canonical_name, db, limit=5)

    if not results or (results and results[0].score < 0.6):
        raw_results = await hybrid_search(raw_detection, db, limit=3)
        seen = {r.food.id for r in results}
        for r in raw_results:
            if r.food.id not in seen:
                results.append(r)

    results = sorted(results, key=lambda r: r.score, reverse=True)[:5]

    return FoodMatch(
        canonical_name=canonical_name,
        canonicalization_confidence=canon_conf,
        search_results=results,
    )
