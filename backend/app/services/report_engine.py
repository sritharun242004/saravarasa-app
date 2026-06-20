"""
Sarvarasa Challenge Report Engine
Generates food-awareness observations, not calorie reports.
"""
from typing import Dict, List


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------

def _food_observations(pct: Dict[str, float], completed_days: int) -> List[str]:
    obs = []
    if pct.get("PROTEIN_PRESENT", 0) >= 60:
        obs.append("You regularly included protein sources in your meals — a great habit for sustained energy.")
    elif pct.get("PROTEIN_PRESENT", 0) >= 30:
        obs.append("Protein was present in some meals. Including it in every main meal helps with fullness and energy.")
    else:
        obs.append("Very few meals had identifiable protein. Adding dal, curd, eggs, or legumes to each meal can make a big difference.")

    if pct.get("VEGETABLE_PRESENT", 0) >= 60:
        obs.append("Vegetables appeared in most of your meals — excellent for gut health, vitamins, and minerals.")
    elif pct.get("VEGETABLE_PRESENT", 0) >= 30:
        obs.append("Vegetables showed up occasionally. Aim to include at least one vegetable in every lunch and dinner.")
    else:
        obs.append("Vegetables were largely absent from your meals. Even a small portion of greens or sabzi counts.")

    if pct.get("FRUIT_PRESENT", 0) >= 40:
        obs.append("Fruits appeared regularly — a wonderful source of natural sugars, fibre, and micronutrients.")
    else:
        obs.append("Fruits were infrequent. One fruit a day as a snack or with breakfast is an easy way to start.")

    if pct.get("TRADITIONAL_FOOD", 0) >= 50:
        obs.append("Your meals were rooted in traditional Indian cooking — these foods tend to be wholesome and well-balanced.")

    if pct.get("PROCESSED_FOOD", 0) >= 30:
        obs.append("Processed or packaged foods appeared in several meals. These tend to be low in fibre and nutrients.")

    if pct.get("SUGARY_BEVERAGE", 0) >= 40:
        obs.append("Sugary beverages (tea, coffee, cold drinks) were a frequent part of meals. Reducing sugar in beverages is a high-impact change.")

    if pct.get("BALANCED_MEAL", 0) >= 50:
        obs.append("Many of your meals showed a good balance of protein and vegetables — the hallmark of a wholesome plate.")

    return obs


def _strengths(compliance_pct: float, pct: Dict[str, float], completed_days: int) -> List[str]:
    out = []
    if compliance_pct >= 100:
        out.append("Outstanding — you completed every single day of the challenge.")
    elif compliance_pct >= 85:
        out.append(f"Strong commitment — you completed {completed_days} out of 7 days consistently.")
    if pct.get("PROTEIN_PRESENT", 0) >= 60:
        out.append("Good habit of including protein in your meals.")
    if pct.get("VEGETABLE_PRESENT", 0) >= 60:
        out.append("Regular inclusion of vegetables shows a health-conscious approach.")
    if pct.get("TRADITIONAL_FOOD", 0) >= 50:
        out.append("You stuck to traditional, home-style Indian foods — these are nutritionally sound.")
    if pct.get("BALANCED_MEAL", 0) >= 50:
        out.append("A good proportion of your meals were balanced with both protein and vegetables.")
    if not out:
        out.append("You completed the challenge and showed up for your health — that in itself is a strength.")
    return out


def _improvements(pct: Dict[str, float]) -> List[str]:
    out = []
    if pct.get("PROTEIN_PRESENT", 0) < 50:
        out.append("Include a protein source (dal, eggs, curd, paneer, chicken) in every main meal.")
    if pct.get("VEGETABLE_PRESENT", 0) < 50:
        out.append("Add at least one vegetable portion to lunch and dinner — even a simple sabzi counts.")
    if pct.get("FRUIT_PRESENT", 0) < 30:
        out.append("Try adding one fruit daily as a mid-morning snack or before a meal.")
    if pct.get("PROCESSED_FOOD", 0) > 30:
        out.append("Reduce packaged or processed snacks — replace with roasted nuts, fruits, or homemade options.")
    if pct.get("SUGARY_BEVERAGE", 0) > 40:
        out.append("Cut down on sweetened tea, coffee, and cold drinks — try reducing sugar gradually.")
    if pct.get("FIBER_SOURCE", 0) < 30:
        out.append("Include more fibre-rich foods: whole grains, ragi, oats, or leafy greens.")
    return out


def _wholesome_plate_tips() -> List[str]:
    return [
        "Fill half your plate with vegetables and greens.",
        "One quarter of your plate should be a whole grain — rice, roti, ragi, or millet.",
        "One quarter should be a protein — dal, curd, egg, chicken, or paneer.",
        "Include one fruit every day as a snack or alongside breakfast.",
        "Drink water before meals — it supports digestion and reduces overeating.",
        "Eat at regular times each day to support your body's natural rhythm.",
        "Traditional Indian foods like idli, sambar, and rasam are naturally wholesome — trust them.",
    ]


def _action_plan(improvements: List[str]) -> List[str]:
    plan = []
    for imp in improvements:
        if "protein" in imp.lower():
            plan.append("Add one protein-rich food to every meal this week — dal, eggs, curd, or legumes.")
        elif "vegetable" in imp.lower():
            plan.append("Cook one extra vegetable dish each day — it doesn't need to be elaborate.")
        elif "fruit" in imp.lower():
            plan.append("Keep one fruit visible on your table as a daily reminder to eat it.")
        elif "processed" in imp.lower():
            plan.append("Replace one packaged snack with a handful of nuts or a fruit this week.")
        elif "sugary" in imp.lower():
            plan.append("Try drinking your morning tea/coffee with half the usual sugar for one week.")
        elif "fibre" in imp.lower():
            plan.append("Swap white rice for brown rice or add ragi to one meal each day.")
    if not plan:
        plan.append("Maintain your current wholesome habits and continue daily meal awareness.")
        plan.append("Explore adding one new vegetable or grain to your meals each week.")
    return plan


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_report(
    client_name: str,
    compliance_pct: float,
    completed_days: int,
    food_pattern_pct: Dict[str, float],
    qualification_status: str,
    eligibility_score: float = 0.0,
    eligibility_band: str = "NOT_READY",
    # legacy fields kept for backward compat
    nutrition: Dict = None,
    pattern: str = "BALANCED",
    days_in_challenge: int = 7,
) -> Dict:
    observations = _food_observations(food_pattern_pct, completed_days)
    improvements = _improvements(food_pattern_pct)

    return {
        "client_name": client_name,
        "compliance_score": compliance_pct,
        "completed_days": completed_days,
        "qualification_status": qualification_status,
        "eligibility_score": eligibility_score,
        "eligibility_band": eligibility_band,
        "food_observations": observations,
        "strengths": _strengths(compliance_pct, food_pattern_pct, completed_days),
        "improvement_areas": improvements,
        "action_plan": _action_plan(improvements),
        "wholesome_plate_tips": _wholesome_plate_tips(),
        "food_pattern_summary": food_pattern_pct,
    }
