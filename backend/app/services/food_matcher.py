"""
Match free-text food names to INDB entries and return nutrition scaled by quantity.
Thin wrapper around the existing indb_engine.
"""
from typing import Optional, Dict
from app.services.nutrition.indb_engine import get_food_unit_nutrition

_NUTRITION_KEYS = [
    "calories", "protein", "carbs", "fat", "fibre",
    "calcium", "iron", "vitamin_c", "potassium", "sodium",
]


def match_food(food_name: str, quantity: float = 1.0) -> Optional[Dict]:
    """
    Return nutrition for food_name scaled by quantity.
    Returns None if no INDB match found.
    """
    base = get_food_unit_nutrition(food_name)
    if base is None:
        return None

    result: Dict = {
        "food_name": food_name,
        "matched_name": base["food_name"],
        "quantity": quantity,
    }
    for key in _NUTRITION_KEYS:
        result[key] = round(base.get(key, 0.0) * quantity, 2)

    return result
