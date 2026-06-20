"""
Knowledge Graph Retrieval Service.
Fetches a fully-hydrated food node with all edges:
  category, region, meal_type, aliases, ingredients, nutrients, related foods.
"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.models.knowledge_graph import Food, FoodNutrient, Nutrient, FoodAlias


# Nutrient name → schema key mapping (INDB column → API field)
_NUTRIENT_MAP = {
    "energy_kcal": "total_calories",
    "protein_g": "protein_g",
    "carb_g": "carbs_g",
    "fat_g": "fat_g",
    "fibre_g": "fiber_g",
    "calcium_mg": "calcium_mg",
    "iron_mg": "iron_mg",
    "vitc_mg": "vitamin_c_mg",
    "potassium_mg": "potassium_mg",
    "sodium_mg": "sodium_mg",
    "vita_ug": "vitamin_a_ug",
}


async def get_food_node(food_id: str, db: AsyncSession) -> Optional[dict]:
    """
    Return a fully-hydrated food node dict for the given UUID.
    """
    stmt = (
        select(Food)
        .options(
            selectinload(Food.category),
            selectinload(Food.region),
            selectinload(Food.meal_type),
            selectinload(Food.aliases),
            selectinload(Food.food_ingredients),
            selectinload(Food.food_nutrients).selectinload(FoodNutrient.nutrient),
        )
        .where(Food.id == food_id)
    )
    food = (await db.execute(stmt)).scalar_one_or_none()
    if not food:
        return None

    # Build nutrient dict keyed by nutrient name
    nutrients_raw: dict[str, float] = {}
    for fn in food.food_nutrients:
        nutrients_raw[fn.nutrient.name] = fn.value_per_100g

    return {
        "id": food.id,
        "name": food.name,
        "canonical_name": food.canonical_name,
        "description": food.description,
        "category": food.category.name if food.category else None,
        "region": food.region.name if food.region else None,
        "meal_type": food.meal_type.name if food.meal_type else None,
        "aliases": [a.alias for a in food.aliases],
        "nutrients_per_100g": nutrients_raw,
        "indb_code": food.indb_code,
    }


async def get_related_foods(food_id: str, db: AsyncSession, limit: int = 5) -> list[dict]:
    """
    Find related foods using pgvector cosine similarity on the same food embedding.
    """
    # Get the source food's embedding
    food = await db.get(Food, food_id)
    if not food or food.embedding is None:
        return []

    vec_str = "[" + ",".join(str(v) for v in food.embedding) + "]"

    stmt = text("""
        SELECT
            f.id,
            f.canonical_name,
            1 - (f.embedding <=> CAST(:vec AS vector)) AS score
        FROM foods f
        WHERE f.id != :food_id
          AND f.embedding IS NOT NULL
        ORDER BY f.embedding <=> CAST(:vec AS vector)
        LIMIT :limit
    """)

    rows = (await db.execute(stmt, {
        "vec": vec_str,
        "food_id": food_id,
        "limit": limit,
    })).all()

    return [
        {"food_id": str(r.id), "name": r.canonical_name, "score": round(float(r.score), 4)}
        for r in rows
    ]


async def get_nutrition_from_graph(food_id: str, db: AsyncSession) -> dict:
    """
    Retrieve nutrition data from the graph (PostgreSQL) — never touches Excel.
    Returns per-100g nutrient values indexed by INDB column name.
    """
    stmt = (
        select(FoodNutrient, Nutrient)
        .join(Nutrient, FoodNutrient.nutrient_id == Nutrient.id)
        .where(FoodNutrient.food_id == food_id)
    )
    rows = (await db.execute(stmt)).all()

    result: dict[str, float] = {}
    for fn, nutrient in rows:
        result[nutrient.name] = fn.value_per_100g

    return result
