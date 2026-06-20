"""
Smart question engine — generates ≤3 targeted questions per detected food.
Questions are context-aware: a biryani gets different questions than a dosa.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Question:
    id: str
    question: str
    options: List[str]
    food_name: str
    reasoning: str = ""


# ── Static question library ────────────────────────────────────────────────────

_QUANTITY_QUESTION = lambda food: Question(
    id="q_quantity",
    question=f"How much {food} did you have?",
    options=["Half portion", "One portion", "Two portions", "More than two portions"],
    food_name=food,
    reasoning="Portion size is the primary driver of calorie variance.",
)

_PREP_QUESTION = lambda food: Question(
    id="q_prep",
    question=f"Where was your {food} prepared?",
    options=["Homemade (less oil)", "Restaurant (regular oil)", "Street food / Dhaba (more oil)"],
    food_name=food,
    reasoning="Cooking method significantly changes fat content.",
)

_CHUTNEY_Q = Question(
    id="q_accomp_south",
    question="What accompaniments did you have?",
    options=["None", "Coconut chutney only", "Sambar + chutney", "Full set (sambar, chutney, rice)"],
    food_name="accompaniments",
    reasoning="South Indian accompaniments add 40-200 kcal.",
)

_RICE_SIZE_Q = Question(
    id="q_quantity",
    question="How much rice did you have?",
    options=["Small bowl (~150g)", "Medium plate (~250g)", "Large plate (~400g)", "Full meal (~600g)"],
    food_name="rice",
    reasoning="Rice portion is highly variable.",
)

_CURRY_SIZE_Q = lambda food: Question(
    id="q_quantity",
    question=f"How much {food} did you have?",
    options=["Side portion (~80g)", "Small serving (~150g)", "Regular serving (~200g)", "Large serving (~300g)"],
    food_name=food,
    reasoning="Curry portion varies widely.",
)

_BIRYANI_Q = Question(
    id="q_biryani_portion",
    question="What size biryani did you have?",
    options=["Half plate (~200g)", "One plate (~350g)", "Full meal (~500g)", "Extra large (~700g)"],
    food_name="biryani",
    reasoning="Biryani portion varies significantly by restaurant.",
)

_BREAD_Q = lambda food: Question(
    id="q_quantity",
    question=f"How many {food} did you eat?",
    options=["1 piece", "2 pieces", "3 pieces", "4 or more"],
    food_name=food,
    reasoning="Each roti/chapati adds ~80-100 kcal.",
)

_GHEE_Q = Question(
    id="q_ghee",
    question="Was extra ghee or butter added?",
    options=["No ghee", "A little (1 tsp)", "Regular (2 tsp)", "Generous (3+ tsp)"],
    food_name="ghee",
    reasoning="1 tsp ghee adds ~45 kcal.",
)

_SUGAR_BEVERAGE_Q = Question(
    id="q_sugar",
    question="How sweet was your drink?",
    options=["No sugar", "Less sweet (1 tsp)", "Regular sweet (2 tsp)", "Extra sweet (3+ tsp)"],
    food_name="beverage",
    reasoning="Sugar significantly changes calorie content of beverages.",
)

_SNACK_Q = lambda food: Question(
    id="q_quantity",
    question=f"How many {food} did you have?",
    options=["2-3 pieces", "4-5 pieces", "6-8 pieces", "More than 8"],
    food_name=food,
    reasoning="Snack portions vary widely.",
)


# ── Category-to-question mapping ───────────────────────────────────────────────

def generate_questions(
    food_name: str,
    category: Optional[str] = None,
    region: Optional[str] = None,
    confidence: float = 1.0,
) -> List[Question]:
    """
    Return ≤3 targeted questions based on food type.
    """
    display = food_name.title()
    cat = (category or "").lower()
    name_lower = food_name.lower()

    questions: List[Question] = []

    # ── Biryani ───────────────────────────────────────────────────────────────
    if "biryani" in name_lower or "biriyani" in name_lower:
        questions = [_BIRYANI_Q, _PREP_QUESTION(display), _GHEE_Q]

    # ── Dosa family ───────────────────────────────────────────────────────────
    elif any(k in name_lower for k in ["dosa", "dose", "dosai", "uttapam"]):
        count_q = Question(
            id="q_quantity",
            question=f"How many {display} did you eat?",
            options=["Half", "One", "Two", "Three or more"],
            food_name=display,
        )
        questions = [count_q, _PREP_QUESTION(display), _CHUTNEY_Q]

    # ── Idli ──────────────────────────────────────────────────────────────────
    elif "idli" in name_lower:
        count_q = Question(
            id="q_quantity",
            question="How many idlis did you have?",
            options=["2 idlis", "4 idlis", "6 idlis", "8 or more"],
            food_name="Idli",
        )
        questions = [count_q, _CHUTNEY_Q, _PREP_QUESTION("idli")]

    # ── Upma / Pongal ─────────────────────────────────────────────────────────
    elif any(k in name_lower for k in ["upma", "pongal", "khichdi", "halwa"]):
        bowl_q = Question(
            id="q_quantity",
            question=f"How much {display} did you eat?",
            options=["Small bowl (~150g)", "Medium bowl (~250g)", "Large bowl (~350g)"],
            food_name=display,
        )
        questions = [bowl_q, _PREP_QUESTION(display), _GHEE_Q]

    # ── Rice dishes ───────────────────────────────────────────────────────────
    elif "rice" in name_lower or "sadam" in name_lower or "chawal" in name_lower:
        questions = [_RICE_SIZE_Q, _PREP_QUESTION(display)]
        if any(k in name_lower for k in ["curd", "lemon", "tamarind"]):
            pass  # no ghee question for these
        else:
            questions.append(_GHEE_Q)

    # ── Bread family ──────────────────────────────────────────────────────────
    elif any(k in name_lower for k in ["chapati", "roti", "paratha", "parantha",
                                        "naan", "puri", "poori", "bhatura"]):
        questions = [_BREAD_Q(display), _PREP_QUESTION(display), _GHEE_Q]

    # ── Curry / Dal / Paneer ──────────────────────────────────────────────────
    elif cat in ("curry",) or any(k in name_lower for k in ["dal", "paneer", "rajma", "chole",
                                                              "sambar", "rasam", "curry"]):
        questions = [_CURRY_SIZE_Q(display), _PREP_QUESTION(display)]

    # ── Beverages ─────────────────────────────────────────────────────────────
    elif cat == "beverage" or any(k in name_lower for k in ["chai", "tea", "coffee", "lassi", "juice"]):
        size_q = Question(
            id="q_quantity",
            question=f"How large was your {display}?",
            options=["Small cup (100ml)", "Regular cup (150ml)", "Large cup (250ml)", "Two cups (300ml)"],
            food_name=display,
        )
        questions = [size_q, _SUGAR_BEVERAGE_Q]

    # ── Snacks ────────────────────────────────────────────────────────────────
    elif cat == "snack" or any(k in name_lower for k in ["vada", "bajji", "pakora", "bonda",
                                                           "bhel", "puri", "chaat"]):
        questions = [_SNACK_Q(display), _PREP_QUESTION(display)]

    # ── Generic fallback ──────────────────────────────────────────────────────
    else:
        questions = [_QUANTITY_QUESTION(display), _PREP_QUESTION(display)]

    return questions[:3]
