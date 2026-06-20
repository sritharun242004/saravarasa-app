"""
Aggregate all meal logs for a client into 7-day nutrition totals and macro percentages.
"""
from typing import List, Dict
from app.services.meal_parser import parse_meal_text
from app.services.food_matcher import match_food


def aggregate_meal_logs(meal_logs: List) -> Dict:
    """
    Parse every meal log text, match foods to INDB, and sum nutrition.
    Returns totals + macro percentages.
    """
    totals = dict(calories=0.0, protein=0.0, carbs=0.0, fat=0.0, fiber=0.0)
    matched_count = 0
    unmatched_count = 0

    for log in meal_logs:
        for item in parse_meal_text(log.meal_text):
            result = match_food(item["food_name"], item["quantity"])
            if result:
                totals["calories"] += result["calories"]
                totals["protein"] += result["protein"]
                totals["carbs"] += result["carbs"]
                totals["fat"] += result["fat"]
                totals["fiber"] += result.get("fibre", 0.0)
                matched_count += 1
            else:
                unmatched_count += 1

    # Round totals
    totals = {k: round(v, 1) for k, v in totals.items()}

    # Macro percentages (by calories)
    cal_from_macros = (totals["protein"] * 4) + (totals["carbs"] * 4) + (totals["fat"] * 9)
    if cal_from_macros > 0:
        totals["protein_pct"] = round(totals["protein"] * 4 / cal_from_macros * 100, 1)
        totals["carb_pct"] = round(totals["carbs"] * 4 / cal_from_macros * 100, 1)
        totals["fat_pct"] = round(totals["fat"] * 9 / cal_from_macros * 100, 1)
    else:
        totals["protein_pct"] = totals["carb_pct"] = totals["fat_pct"] = 0.0

    totals["matched_foods"] = matched_count
    totals["unmatched_foods"] = unmatched_count
    return totals
