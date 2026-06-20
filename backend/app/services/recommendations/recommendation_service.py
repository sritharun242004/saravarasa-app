"""
Recommendation service — returns similar foods as healthier alternatives.
Uses pgvector similarity + nutrient-based filtering.
"""
from __future__ import annotations
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.models.knowledge_graph import Food, FoodNutrient, Nutrient
from app.services.knowledge_graph.graph_service import get_related_foods, get_nutrition_from_graph


async def get_recommendations(
    food_id: str,
    db: AsyncSession,
    goal: str = "weight_loss",  # weight_loss | muscle_gain | diabetic | heart_health
    limit: int = 4,
) -> List[dict]:
    """
    Find similar foods (by embedding) and score them for the given health goal.
    """
    related = await get_related_foods(food_id, db, limit=limit * 2)
    if not related:
        return []

    scored: List[dict] = []
    for item in related:
        nutrients = await get_nutrition_from_graph(item["food_id"], db)
        if not nutrients:
            continue

        cal = nutrients.get("energy_kcal", 0)
        protein = nutrients.get("protein_g", 0)
        carbs = nutrients.get("carb_g", 0)
        fat = nutrients.get("fat_g", 0)
        fiber = nutrients.get("fibre_g", 0)

        if goal == "weight_loss":
            goal_score = max(0, 100 - cal / 5 + fiber * 5 - fat)
        elif goal == "muscle_gain":
            goal_score = min(100, protein * 4 + (cal / 10))
        elif goal == "diabetic":
            goal_score = max(0, 100 - carbs * 0.8 + fiber * 6 - fat * 0.5)
        elif goal == "heart_health":
            sodium = nutrients.get("sodium_mg", 0)
            goal_score = max(0, 100 - sodium / 20 - fat + fiber * 3)
        else:
            goal_score = 50.0

        scored.append({
            **item,
            "goal_score": round(goal_score, 1),
            "calories_per_100g": round(cal, 1),
            "protein_per_100g": round(protein, 1),
        })

    scored.sort(key=lambda x: x["goal_score"], reverse=True)
    return scored[:limit]
