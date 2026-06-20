"""
Sarvarasa compliance: a day is complete only when Breakfast + Lunch + Dinner
are all submitted (with image + text). Snack is optional.

Pass threshold: 6 out of 7 days completed  (≈ 85.7%)
"""
from typing import List, Dict

REQUIRED_DAYS = 7
REQUIRED_MEALS_PER_DAY = {"BREAKFAST", "LUNCH", "DINNER"}
PASS_THRESHOLD = 85.0


def _completed_days(meal_logs: List) -> Dict[int, set]:
    """Return {day_number: set_of_meal_types} for all submitted logs."""
    days: Dict[int, set] = {}
    for log in meal_logs:
        days.setdefault(log.day_number, set())
        days[log.day_number].add(log.meal_type.upper())
    return days


def calculate_compliance(meal_logs: List) -> Dict:
    days_map = _completed_days(meal_logs)

    completed = [
        d for d, types in days_map.items()
        if REQUIRED_MEALS_PER_DAY.issubset(types)
    ]
    completed_count = len(completed)
    pct = round((completed_count / REQUIRED_DAYS) * 100, 1)

    missed_days = sorted(d for d in range(1, REQUIRED_DAYS + 1) if d not in completed)

    # Longest streak of fully missed consecutive days
    all_days = set(days_map.keys())
    max_consecutive = 0
    run = 0
    for d in range(1, REQUIRED_DAYS + 1):
        if d not in all_days:
            run += 1
            max_consecutive = max(max_consecutive, run)
        else:
            run = 0

    if completed_count == REQUIRED_DAYS:
        status = "COMPLETE"
    elif pct >= PASS_THRESHOLD:
        status = "QUALIFIED"
    else:
        status = "FAILED"

    return {
        "required_days": REQUIRED_DAYS,
        "completed_days": completed_count,
        "compliance_pct": pct,
        "status": status,
        "max_consecutive_missed_days": max_consecutive,
        "missed_days": missed_days,
        "days_detail": {
            d: list(types) for d, types in sorted(days_map.items())
        },
        # legacy field kept for backward compat
        "submitted_meals": len(meal_logs),
        "required_meals": REQUIRED_DAYS * 3,
    }
