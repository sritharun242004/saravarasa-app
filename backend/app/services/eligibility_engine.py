"""
Calculate the weighted eligibility score (0–100) and assign a band.

Weights:
  Compliance   40 %
  Meal Quality 30 %
  Consistency  20 %
  Engagement   10 %
"""
from typing import Dict

BANDS = {
    "GOLD":      (90, 101),
    "STRONG":    (80, 90),
    "MODERATE":  (70, 80),
    "NOT_READY": (0,  70),
}

BAND_LABELS = {
    "GOLD":      "Gold Candidate",
    "STRONG":    "Strong Candidate",
    "MODERATE":  "Moderate",
    "NOT_READY": "Not Ready",
}


def calculate_eligibility(
    compliance_pct: float,
    protein_pct: float,
    avg_daily_fiber: float,
    avg_daily_calories: float,
    submitted_days: int,
    submitted_meals: int,
) -> Dict:
    # 1. Compliance (40 pts)
    compliance_score = min(compliance_pct, 100) * 0.40

    # 2. Meal Quality (30 pts): protein adequacy + fibre + calorie range
    protein_score = min(protein_pct / 20 * 100, 100)       # 20 % protein = full score
    fiber_score = min(avg_daily_fiber / 25 * 100, 100)      # 25 g/day = full score
    calorie_ideal = 1800
    calorie_score = max(0.0, 100 - abs(avg_daily_calories - calorie_ideal) / 10)
    quality_score = (protein_score + fiber_score + calorie_score) / 3 * 0.30

    # 3. Consistency (20 pts): how many of 7 days had at least one meal
    consistency_score = min(submitted_days / 7 * 100, 100) * 0.20

    # 4. Engagement (10 pts): fraction of 21 meals actually submitted
    engagement_score = min(submitted_meals / 21 * 100, 100) * 0.10

    total = round(compliance_score + quality_score + consistency_score + engagement_score, 1)

    band = "NOT_READY"
    for b, (lo, hi) in BANDS.items():
        if lo <= total < hi:
            band = b
            break

    return {
        "eligibility_score": total,
        "eligibility_band": band,
        "breakdown": {
            "compliance": round(compliance_score, 1),
            "meal_quality": round(quality_score, 1),
            "consistency": round(consistency_score, 1),
            "engagement": round(engagement_score, 1),
        },
    }
