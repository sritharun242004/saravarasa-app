"""
Sarvarasa Food Pattern Engine
Classifies each meal based on FOOD PRESENCE, not macros or calories.

Philosophy: understand what people eat, not how many calories they consume.
"""
from typing import List, Dict, Set

# Keyword banks
PROTEIN_KEYWORDS = {
    "egg", "eggs", "chicken", "fish", "dal", "dhal", "lentil", "rajma", "chana",
    "paneer", "tofu", "curd", "yogurt", "dahi", "thayir", "milk", "paal",
    "mutton", "beef", "pork", "prawn", "shrimp", "soya", "groundnut", "peanut",
    "moong", "urad", "masoor", "kadala", "payar", "chickpea", "soybean",
    "whey", "protein", "nuts", "cashew", "almond", "walnut",
}

VEGETABLE_KEYWORDS = {
    "keerai", "spinach", "greens", "tomato", "onion", "carrot", "beans", "drumstick",
    "broccoli", "cauliflower", "cabbage", "potato", "sweet potato", "ladies finger",
    "okra", "bhindi", "pumpkin", "gourd", "ridge gourd", "bitter gourd", "eggplant",
    "brinjal", "capsicum", "pepper", "peas", "corn", "beetroot", "radish",
    "cucumber", "salad", "lettuce", "methi", "fenugreek", "palak", "mixed veg",
    "veggie", "vegetable", "sabzi", "kootu", "poriyal", "thoran", "avial",
    "sambar", "rasam", "moringa", "curry leaves",
}

FRUIT_KEYWORDS = {
    "apple", "banana", "mango", "papaya", "guava", "orange", "grapes", "watermelon",
    "pineapple", "pomegranate", "strawberry", "blueberry", "melon", "fig",
    "dates", "plum", "peach", "pear", "lemon", "lime", "coconut", "tender coconut",
    "jackfruit", "jamun", "gooseberry", "amla", "fruit salad", "fruit",
}

PROCESSED_FOOD_KEYWORDS = {
    "biscuit", "cookie", "chips", "namkeen", "snack pack", "maggi", "noodles",
    "instant", "frozen", "packaged", "bread", "white bread", "maida",
    "pizza", "burger", "sandwich", "fast food", "kfc", "mcdonalds",
    "sausage", "salami", "bacon", "spam", "ready to eat", "processed",
    "refined", "puri", "bhatura", "samosa", "vada pav", "pav bhaji",
}

SUGARY_BEVERAGE_KEYWORDS = {
    "tea", "chai", "coffee", "cold drink", "soda", "pepsi", "cola", "sprite",
    "juice", "squash", "energy drink", "health drink", "horlicks", "bournvita",
    "milk powder", "flavored milk", "chocolate milk", "milkshake", "lassi sweet",
    "sugarcane juice", "fruit punch", "lemonade sweet",
}

TRADITIONAL_FOOD_KEYWORDS = {
    "idli", "idly", "dosa", "uttapam", "upma", "pongal", "venpongal", "ven pongal",
    "kozhukattai", "puttu", "appam", "idiyappam", "string hoppers", "pesarattu",
    "ragi", "jowar", "bajra", "millet", "foxtail millet", "little millet",
    "rice", "sadham", "soru", "sambar", "rasam", "avial", "kootu", "thoran",
    "poriyal", "keerai", "mor kuzhambu", "tamarind rice", "lemon rice",
    "curd rice", "thayir sadam", "biryani", "khichdi", "dal khichdi",
    "roti", "chapati", "phulka", "paratha", "sabzi",
}

FIBER_SOURCE_KEYWORDS = {
    "oats", "oatmeal", "whole wheat", "brown rice", "ragi", "jowar", "bajra",
    "millets", "lentils", "beans", "chickpea", "rajma", "green peas", "leafy",
    "greens", "vegetables", "fruits", "flaxseed", "chia", "psyllium",
    "bran", "whole grain", "multigrain",
}


def _normalize(text: str) -> str:
    return text.lower().strip()


def classify_meal(meal_text: str) -> Dict[str, bool]:
    """Return a dict of food pattern tags for a single meal."""
    text = _normalize(meal_text)
    words = set(text.replace(",", " ").replace("+", " ").split())
    # Also check for multi-word phrases
    full = text

    def has_any(keywords: Set[str]) -> bool:
        for kw in keywords:
            if kw in full:
                return True
        return False

    tags = {
        "PROTEIN_PRESENT": has_any(PROTEIN_KEYWORDS),
        "VEGETABLE_PRESENT": has_any(VEGETABLE_KEYWORDS),
        "FRUIT_PRESENT": has_any(FRUIT_KEYWORDS),
        "FIBER_SOURCE": has_any(FIBER_SOURCE_KEYWORDS),
        "TRADITIONAL_FOOD": has_any(TRADITIONAL_FOOD_KEYWORDS),
        "PROCESSED_FOOD": has_any(PROCESSED_FOOD_KEYWORDS),
        "SUGARY_BEVERAGE": has_any(SUGARY_BEVERAGE_KEYWORDS),
    }

    # Balanced meal: has protein + vegetable, no processed food
    tags["BALANCED_MEAL"] = (
        tags["PROTEIN_PRESENT"] and
        tags["VEGETABLE_PRESENT"] and
        not tags["PROCESSED_FOOD"]
    )

    return tags


def aggregate_patterns(meal_logs: List) -> Dict:
    """
    Aggregate food pattern tags across all 7-day meal logs.
    Returns counts, percentages, and a summary assessment.
    """
    total = len(meal_logs)
    if total == 0:
        return {
            "total_meals": 0,
            "counts": {},
            "percentages": {},
            "assessment": "No meals logged yet.",
        }

    tag_counts: Dict[str, int] = {
        "PROTEIN_PRESENT": 0,
        "VEGETABLE_PRESENT": 0,
        "FRUIT_PRESENT": 0,
        "FIBER_SOURCE": 0,
        "TRADITIONAL_FOOD": 0,
        "PROCESSED_FOOD": 0,
        "SUGARY_BEVERAGE": 0,
        "BALANCED_MEAL": 0,
    }

    for log in meal_logs:
        tags = classify_meal(log.meal_text)
        for tag, present in tags.items():
            if present and tag in tag_counts:
                tag_counts[tag] += 1

    pct = {k: round(v / total * 100, 1) for k, v in tag_counts.items()}

    return {
        "total_meals": total,
        "counts": tag_counts,
        "percentages": pct,
    }
