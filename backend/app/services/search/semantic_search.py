"""
pgvector semantic search over foods.embedding using cosine distance.
Target: <100 ms per query.
"""
from __future__ import annotations
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.models.knowledge_graph import Food, FoodAlias, Category, Region, MealType
from app.services.embeddings.embedding_service import embed_query


class SemanticSearchResult:
    __slots__ = ("food", "score", "matched_alias")

    def __init__(self, food: Food, score: float, matched_alias: str | None = None):
        self.food = food
        self.score = score
        self.matched_alias = matched_alias

    def to_dict(self) -> dict:
        return {
            "food_id": self.food.id,
            "name": self.food.canonical_name,
            "display_name": self.matched_alias or self.food.canonical_name,
            "score": round(self.score, 4),
            "category": self.food.category.name if self.food.category else None,
            "region": self.food.region.name if self.food.region else None,
            "meal_type": self.food.meal_type.name if self.food.meal_type else None,
        }


async def semantic_search(
    query: str,
    db: AsyncSession,
    limit: int = 5,
    threshold: float = 0.30,   # cosine distance; lower = more similar
) -> List[SemanticSearchResult]:
    """
    Embed the query text and find the closest food vectors in PostgreSQL.
    Uses pgvector's <=> cosine distance operator via raw SQL for performance.
    """
    vec = await embed_query(query)
    vec_str = "[" + ",".join(str(v) for v in vec) + "]"

    # Raw SQL is faster than ORM for the vector op; we still map to ORM objects
    stmt = text("""
        SELECT
            f.id,
            1 - (f.embedding <=> CAST(:vec AS vector)) AS score
        FROM foods f
        WHERE f.embedding IS NOT NULL
          AND 1 - (f.embedding <=> CAST(:vec AS vector)) >= :threshold
        ORDER BY f.embedding <=> CAST(:vec AS vector)
        LIMIT :limit
    """)

    rows = (await db.execute(stmt, {"vec": vec_str, "threshold": threshold, "limit": limit})).all()

    if not rows:
        return []

    food_ids = [str(r.id) for r in rows]
    score_map = {str(r.id): float(r.score) for r in rows}

    foods_q = (
        select(Food)
        .options(
            selectinload(Food.category),
            selectinload(Food.region),
            selectinload(Food.meal_type),
            selectinload(Food.aliases),
        )
        .where(Food.id.in_(food_ids))
    )
    foods = (await db.execute(foods_q)).scalars().all()

    results = []
    for food in sorted(foods, key=lambda f: score_map.get(str(f.id), 0), reverse=True):
        results.append(SemanticSearchResult(food, score_map.get(str(food.id), 0)))

    return results


async def alias_search(
    query: str,
    db: AsyncSession,
    limit: int = 5,
) -> List[SemanticSearchResult]:
    """
    Exact + partial alias text match as a fast pre-pass before semantic search.
    Avoids embedding cost when a direct alias match exists.
    """
    q = query.strip().lower()

    stmt = (
        select(FoodAlias, Food)
        .join(Food, FoodAlias.food_id == Food.id)
        .options(
            selectinload(Food.category),
            selectinload(Food.region),
            selectinload(Food.meal_type),
        )
        .where(FoodAlias.alias.ilike(f"%{q}%"))
        .order_by(FoodAlias.confidence.desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()

    return [
        SemanticSearchResult(food=food, score=float(alias.confidence), matched_alias=alias.alias)
        for alias, food in rows
    ]


async def name_search(
    query: str,
    db: AsyncSession,
    limit: int = 5,
) -> List[SemanticSearchResult]:
    """Partial name match on foods.name as a fallback when no alias matches."""
    q = query.strip().lower()
    stmt = (
        select(Food)
        .options(
            selectinload(Food.category),
            selectinload(Food.region),
            selectinload(Food.meal_type),
            selectinload(Food.aliases),
        )
        .where(Food.name.ilike(f"%{q}%"))
        .limit(limit)
    )
    foods = (await db.execute(stmt)).scalars().all()
    return [SemanticSearchResult(food=food, score=0.70) for food in foods]


async def hybrid_search(
    query: str,
    db: AsyncSession,
    limit: int = 5,
) -> List[SemanticSearchResult]:
    """
    Alias match first (fast path) → semantic search (if Gemini key present)
    → name search fallback. Deduplicates by food_id throughout.
    """
    alias_hits = await alias_search(query, db, limit=limit)
    seen_ids = {r.food.id for r in alias_hits}

    # Semantic search — gracefully skip if Gemini key missing/invalid
    try:
        semantic_hits = await semantic_search(query, db, limit=limit)
        for r in semantic_hits:
            if r.food.id not in seen_ids:
                alias_hits.append(r)
                seen_ids.add(r.food.id)
    except Exception:
        pass  # No valid embedding key — alias + name search is enough

    # Name search fallback if we still have fewer results than requested
    if len(alias_hits) < limit:
        name_hits = await name_search(query, db, limit=limit)
        for r in name_hits:
            if r.food.id not in seen_ids:
                alias_hits.append(r)
                seen_ids.add(r.food.id)

    return alias_hits[:limit]
