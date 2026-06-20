"""
Classify a client's 7-day eating behaviour into a single named pattern.
"""


PATTERN_LABELS = {
    "BALANCED": "Balanced Diet",
    "CARB_HEAVY": "Carb Heavy",
    "PROTEIN_DEFICIENT": "Protein Deficient",
    "HIGH_CALORIE": "High Calorie Pattern",
    "LOW_FIBER": "Low Fiber",
    "HIGH_SUGAR": "High Sugar",
    "VEGETARIAN_BALANCED": "Vegetarian Balanced",
}


def classify_pattern(
    protein_pct: float,
    carb_pct: float,
    fat_pct: float,
    avg_daily_calories: float,
    avg_daily_fiber: float,
    has_meat: bool = False,
) -> str:
    """
    Returns one of the PATTERN_LABELS keys based on macro ratios and averages.
    Evaluated in priority order — first matching rule wins.
    """
    if avg_daily_calories > 2400:
        return "HIGH_CALORIE"
    if carb_pct > 60:
        return "CARB_HEAVY"
    if protein_pct < 12:
        return "PROTEIN_DEFICIENT"
    if avg_daily_fiber < 15:
        return "LOW_FIBER"
    if 20 <= protein_pct <= 30 and 45 <= carb_pct <= 55 and 20 <= fat_pct <= 30:
        return "BALANCED" if has_meat else "VEGETARIAN_BALANCED"
    return "BALANCED"
