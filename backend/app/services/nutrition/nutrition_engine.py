"""
Nutrition Engine v2 — DB-backed, never reads Excel at runtime.

Pipeline:
  food_id (UUID from semantic search)
  → FoodNutrient rows from PostgreSQL
  → apply portion + cooking multipliers
  → compute health scores
  → return NutritionResult
"""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.knowledge_graph.graph_service import get_nutrition_from_graph

# ── Portion answer → multiplier map ───────────────────────────────────────────

_PORTION_MULT: dict[str, float] = {
    # Quantity
    "half": 0.5, "half portion": 0.5, "half plate (~150g)": 0.5,
    "one": 1.0, "one portion": 1.0, "one plate (~250g)": 1.0,
    "two": 2.0, "two portions": 2.0, "two pieces": 2.0,
    "three or more": 2.5, "more than two portions": 2.5, "4 or more": 3.0,
    # Idli
    "2 idlis": 0.8, "4 idlis": 1.6, "6 idlis": 2.4, "8 or more": 3.5,
    # Bread
    "1 piece": 0.5, "2 pieces": 1.0, "3 pieces": 1.5,
    # Rice
    "small bowl (~150g)": 0.6, "medium plate (~250g)": 1.0, "large plate (~400g)": 1.6, "full meal (~600g)": 2.4,
    # Biryani
    "half plate (~200g)": 0.57, "one plate (~350g)": 1.0, "full meal (~500g)": 1.43, "extra large (~700g)": 2.0,
    # Snacks
    "2-3 pieces": 0.5, "4-5 pieces": 1.0, "6-8 pieces": 1.5, "more than 8": 2.5,
    # Beverage
    "small cup (100ml)": 0.67, "regular cup (150ml)": 1.0, "large cup (250ml)": 1.67, "two cups (300ml)": 2.0,
    # Curry
    "side portion (~80g)": 0.4, "small serving (~150g)": 0.75, "regular serving (~200g)": 1.0, "large serving (~300g)": 1.5,
}

_COOKING_MULT: dict[str, float] = {
    "homemade (less oil)": 0.82,
    "restaurant (regular oil)": 1.0,
    "street food / dhaba (more oil)": 1.20,
    "homemade (light oil)": 0.85,
    "restaurant": 1.0,
    "street food/dhaba": 1.15,
}

_ACCOMP_KCAL: dict[str, float] = {
    "none": 0, "no ghee": 0, "no sugar": 0,
    "coconut chutney only": 35,
    "sambar + chutney": 85,
    "full set (sambar, chutney, rice)": 220,
    "a little (1 tsp)": 45,
    "regular (2 tsp)": 90,
    "generous (3+ tsp)": 135,
    "less sweet (1 tsp)": 16,
    "regular sweet (2 tsp)": 32,
    "extra sweet (3+ tsp)": 50,
}


def _parse_answers(answers: dict[str, str]) -> tuple[float, float, float]:
    """Return (portion_mult, cooking_mult, extra_kcal) from question answers."""
    portion_mult = 1.0
    cooking_mult = 1.0
    extra_kcal = 0.0

    for v in answers.values():
        key = v.lower().strip()
        if key in _PORTION_MULT:
            portion_mult = _PORTION_MULT[key]
        elif key in _COOKING_MULT:
            cooking_mult = _COOKING_MULT[key]
        elif key in _ACCOMP_KCAL:
            extra_kcal += _ACCOMP_KCAL[key]

    return portion_mult, cooking_mult, extra_kcal


def _safe(val) -> float:
    try:
        f = float(val)
        return 0.0 if f != f else f   # NaN → 0
    except (TypeError, ValueError):
        return 0.0


def compute_health_scores(nutrition: dict) -> dict:
    cal = nutrition.get("total_calories", 0)
    protein = nutrition.get("protein_g", 0)
    carbs = nutrition.get("carbs_g", 0)
    fat = nutrition.get("fat_g", 0)
    fiber = nutrition.get("fiber_g", 0)
    sodium = nutrition.get("sodium_mg", 0)

    # Weight loss: reward low-cal, high-fiber; penalise fat
    wl = 100 - max(0, int((cal - 400) / 10)) - (15 if fiber < 2 else 0) - (10 if fat > 25 else 0)

    # Muscle gain: reward high-protein
    mg = 40 + min(50, int(protein * 5)) + (10 if cal > 300 else 0)

    # Diabetic: penalise high carbs, reward fiber
    db = 100 - max(0, int((carbs - 40) * 1.5)) + (10 if fiber >= 3 else 0) - (10 if fat > 20 else 0)

    # Heart health: penalise high sodium and fat
    hh = 100 - max(0, int((sodium - 600) / 15)) - (15 if fat > 20 else 0) + (10 if fiber >= 3 else 0)

    scores = {
        "weight_loss": max(0, min(100, wl)),
        "muscle_gain": max(0, min(100, mg)),
        "diabetic_friendly": max(0, min(100, db)),
        "heart_health": max(0, min(100, hh)),
    }
    scores["overall"] = int(sum(scores.values()) / 4)
    return scores


async def calculate_nutrition(
    food_ids: list[str],
    answers: dict[str, str],
    db: AsyncSession,
) -> dict:
    """
    Retrieve per-100g nutrition for each food from the DB, then apply
    portion/cooking multipliers derived from the user's answers.
    """
    portion_mult, cooking_mult, extra_kcal = _parse_answers(answers)

    totals: dict[str, float] = {
        "total_calories": 0.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0,
        "calcium_mg": 0.0,
        "iron_mg": 0.0,
        "vitamin_c_mg": 0.0,
        "potassium_mg": 0.0,
        "sodium_mg": 0.0,
        "vitamin_a_ug": 0.0,
    }

    for food_id in food_ids:
        raw = await get_nutrition_from_graph(food_id, db)
        if not raw:
            # Fallback for unmatched foods
            totals["total_calories"] += 200 * portion_mult * cooking_mult
            totals["protein_g"] += 6 * portion_mult
            totals["carbs_g"] += 35 * portion_mult
            totals["fat_g"] += 6 * portion_mult * cooking_mult
            totals["fiber_g"] += 2 * portion_mult
            continue

        fat_mult = portion_mult * cooking_mult

        totals["total_calories"] += _safe(raw.get("energy_kcal")) * portion_mult * cooking_mult
        totals["protein_g"]      += _safe(raw.get("protein_g")) * portion_mult
        totals["carbs_g"]        += _safe(raw.get("carb_g")) * portion_mult
        totals["fat_g"]          += _safe(raw.get("fat_g")) * fat_mult
        totals["fiber_g"]        += _safe(raw.get("fibre_g")) * portion_mult
        totals["calcium_mg"]     += _safe(raw.get("calcium_mg")) * portion_mult
        totals["iron_mg"]        += _safe(raw.get("iron_mg")) * portion_mult
        totals["vitamin_c_mg"]   += _safe(raw.get("vitc_mg")) * portion_mult
        totals["potassium_mg"]   += _safe(raw.get("potassium_mg")) * portion_mult
        totals["sodium_mg"]      += _safe(raw.get("sodium_mg")) * portion_mult
        totals["vitamin_a_ug"]   += _safe(raw.get("vita_ug")) * portion_mult

    totals["total_calories"] += extra_kcal

    return {k: round(v, 2) for k, v in totals.items()}
