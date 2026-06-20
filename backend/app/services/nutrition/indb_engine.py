"""
INDB Nutrition Engine - Uses Anuvaad_INDB_2024.11.xlsx dataset
Maps detected food names to INDB entries and calculates nutrition.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache
from app.config import settings

# ── Template-based portion/prep questions (mirrors Streamlit TEMPLATES) ────────
TEMPLATES: dict = {
    "DOSA": {
        "label": "Dosa", "icon": "🫓",
        "questions": [
            {"id": "count", "label": "How many dosas?",
             "options": ["Half", "One", "Two", "Three"],
             "multipliers": {"Half": 0.5, "One": 1.0, "Two": 2.0, "Three": 3.0}},
            {"id": "prep", "label": "Preparation",
             "options": ["Homemade", "Restaurant", "Street Food"],
             "multipliers": {"Homemade": 0.95, "Restaurant": 1.10, "Street Food": 1.05}},
        ],
    },
    "IDLI": {
        "label": "Idli", "icon": "⚪",
        "questions": [
            {"id": "count", "label": "How many idlis?",
             "options": ["1", "2", "3", "4"],
             "multipliers": {"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0}},
            {"id": "size", "label": "Size",
             "options": ["Small", "Medium", "Large"],
             "multipliers": {"Small": 0.75, "Medium": 1.0, "Large": 1.30}},
        ],
    },
    "VADA": {
        "label": "Vada", "icon": "🍩",
        "questions": [
            {"id": "count", "label": "How many vadas?",
             "options": ["1", "2", "3", "4"],
             "multipliers": {"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0}},
            {"id": "prep", "label": "Preparation",
             "options": ["Homemade", "Restaurant", "Street Food"],
             "multipliers": {"Homemade": 0.95, "Restaurant": 1.10, "Street Food": 1.05}},
        ],
    },
    "BIRYANI": {
        "label": "Biryani", "icon": "🍛",
        "questions": [
            {"id": "size", "label": "Serving Size",
             "options": ["Small Bowl", "Medium Bowl", "Large Bowl"],
             "multipliers": {"Small Bowl": 0.75, "Medium Bowl": 1.0, "Large Bowl": 1.50}},
        ],
    },
    "RICE": {
        "label": "Rice", "icon": "🍚",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Quarter Plate", "Half Plate", "Full Plate"],
             "multipliers": {"Quarter Plate": 0.5, "Half Plate": 1.0, "Full Plate": 2.0}},
        ],
    },
    "BEVERAGE": {
        "label": "Beverage", "icon": "☕",
        "questions": [
            {"id": "size", "label": "Cup / Glass Size",
             "options": ["Small", "Medium", "Large"],
             "multipliers": {"Small": 0.75, "Medium": 1.0, "Large": 1.50}},
            {"id": "sugar", "label": "Sugar",
             "options": ["No Sugar", "1 tsp", "2 tsp", "3 tsp"],
             "multipliers": {"No Sugar": 1.0, "1 tsp": 1.06, "2 tsp": 1.12, "3 tsp": 1.18}},
        ],
    },
    "DAL": {
        "label": "Dal / Sambar", "icon": "🍲",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Few Spoons", "Half Bowl", "Full Bowl"],
             "multipliers": {"Few Spoons": 0.5, "Half Bowl": 1.0, "Full Bowl": 2.0}},
            {"id": "prep", "label": "Preparation",
             "options": ["Homemade", "Restaurant"],
             "multipliers": {"Homemade": 0.95, "Restaurant": 1.10}},
        ],
    },
    "BREAD": {
        "label": "Roti / Bread", "icon": "🫓",
        "questions": [
            {"id": "count", "label": "How many?",
             "options": ["1", "2", "3", "4", "5"],
             "multipliers": {"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0, "5": 5.0}},
            {"id": "size", "label": "Size",
             "options": ["Small", "Medium", "Large"],
             "multipliers": {"Small": 0.80, "Medium": 1.0, "Large": 1.25}},
        ],
    },
    "CURRY": {
        "label": "Curry", "icon": "🫕",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Few Spoons", "Half Bowl", "Full Bowl"],
             "multipliers": {"Few Spoons": 0.5, "Half Bowl": 1.0, "Full Bowl": 2.0}},
            {"id": "prep", "label": "Preparation",
             "options": ["Homemade", "Restaurant"],
             "multipliers": {"Homemade": 0.95, "Restaurant": 1.10}},
        ],
    },
    "SNACK": {
        "label": "Snack", "icon": "🧆",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Small Portion", "Medium Portion", "Large Portion"],
             "multipliers": {"Small Portion": 0.5, "Medium Portion": 1.0, "Large Portion": 1.5}},
        ],
    },
    "SWEET": {
        "label": "Sweet / Dessert", "icon": "🍮",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Half", "One", "Two"],
             "multipliers": {"Half": 0.5, "One": 1.0, "Two": 2.0}},
            {"id": "prep", "label": "Source",
             "options": ["Homemade", "Mithai Shop", "Restaurant"],
             "multipliers": {"Homemade": 0.95, "Mithai Shop": 1.0, "Restaurant": 1.10}},
        ],
    },
    "FRUIT": {
        "label": "Fruit", "icon": "🍎",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Half", "One", "Two", "Three"],
             "multipliers": {"Half": 0.5, "One": 1.0, "Two": 2.0, "Three": 3.0}},
        ],
    },
    "NON_VEG": {
        "label": "Non Veg", "icon": "🍗",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Small Portion", "Half Bowl", "Full Bowl"],
             "multipliers": {"Small Portion": 0.75, "Half Bowl": 1.0, "Full Bowl": 1.50}},
            {"id": "prep", "label": "Preparation",
             "options": ["Homemade", "Restaurant"],
             "multipliers": {"Homemade": 0.95, "Restaurant": 1.10}},
        ],
    },
    "VEGETABLE": {
        "label": "Vegetable", "icon": "🥦",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Few Spoons", "Half Bowl", "Full Bowl"],
             "multipliers": {"Few Spoons": 0.5, "Half Bowl": 1.0, "Full Bowl": 2.0}},
            {"id": "prep", "label": "Preparation",
             "options": ["Raw / Salad", "Cooked"],
             "multipliers": {"Raw / Salad": 1.0, "Cooked": 0.90}},
        ],
    },
    "GENERAL": {
        "label": "Food Item", "icon": "🍽️",
        "questions": [
            {"id": "quantity", "label": "Quantity",
             "options": ["Small", "Medium", "Large"],
             "multipliers": {"Small": 0.75, "Medium": 1.0, "Large": 1.50}},
        ],
    },
}

_CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("DOSA",      ["dosa", "dosai", "uttapam", "uttappam", "pesarattu"]),
    ("IDLI",      ["idli", "idly"]),
    ("VADA",      ["vada", "vadai", "vade", "medu"]),
    ("BIRYANI",   ["biryani", "biriyani"]),
    ("BEVERAGE",  ["tea", "coffee", "juice", "milk", "lassi", "chai", "kaapi",
                   "sherbet", "buttermilk", "shake", "drink", "water"]),
    ("DAL",       ["sambar", "rasam", "dal", "dhal", "daal", "soup", "lentil", "paruppu"]),
    ("BREAD",     ["chapati", "chapathi", "roti", "paratha", "parantha", "naan", "puri",
                   "poori", "parotta", "appam", "bhatura", "thepla", "puttu", "bread", "toast"]),
    ("RICE",      ["rice", "pulao", "pulav", "pongal", "khichdi", "upma", "poha", "chawal", "anna"]),
    ("NON_VEG",   ["chicken", "mutton", "fish", "egg", "prawn", "beef", "pork", "meat",
                   "keema", "crab", "seafood", "lamb", "shrimp"]),
    ("SWEET",     ["halwa", "halva", "kheer", "payasam", "ladoo", "laddoo", "barfi", "burfi",
                   "gulab jamun", "rasgulla", "jalebi", "sweet", "cake", "kulfi"]),
    ("FRUIT",     ["apple", "banana", "mango", "orange", "grape", "guava", "papaya",
                   "watermelon", "pineapple", "fruit", "pear", "plum"]),
    ("SNACK",     ["biscuit", "chips", "murukku", "chakli", "popcorn", "pakoda", "pakora",
                   "bajji", "bonda", "samosa", "cutlet", "tikki"]),
    ("CURRY",     ["curry", "masala", "poriyal", "thoran", "sabzi", "sabji", "bhaji",
                   "gravy", "roast", "stir fry", "palak", "paneer", "korma", "kootu", "fry"]),
    ("VEGETABLE", ["vegetable", "greens", "salad", "spinach", "carrot", "beans", "peas",
                   "broccoli", "cauliflower", "cabbage", "brinjal", "eggplant"]),
]


def classify_food(name: str) -> str:
    n = name.lower()
    for template_id, keywords in _CATEGORY_RULES:
        for kw in keywords:
            if kw in n:
                return template_id
    return "GENERAL"

# Portion multipliers based on question answers
PORTION_MULTIPLIERS = {
    # Quantity answers
    "half": 0.5, "half portion": 0.5, "small portion (half plate)": 0.5,
    "one": 1.0, "regular portion (one plate)": 1.0, "regular portion": 1.0,
    "two": 2.0, "large portion (two plates)": 2.0,
    "more than two": 2.5, "more": 2.5,
    # Cooking method multipliers (fat adjustment)
    "homemade (light oil)": 0.85,
    "restaurant": 1.0,
    "restaurant (regular)": 1.0,
    "restaurant (street food)": 1.15,
    "street food/dhaba": 1.15,
    # Accompaniment calorie additions (kcal)
    "none": 0, "no extras": 0,
    "chutney only": 30,
    "sambar + chutney": 80,
    "full set with rice": 200,
    "small portion": 25, "regular portion": 60, "extra": 100,
}

# Food alias mapping: detected name -> INDB food_name search terms
FOOD_ALIASES = {
    # South Indian
    "masala_dosa": ["masala dosa", "masala dose"],
    "plain_dosa": ["plain dosa", "dosa"],
    "rava_dosa": ["semolina dosa", "rava dosa", "suji dosa"],
    "paper_roast": ["paper dosa", "plain dosa"],
    "ghee_dosa": ["ghee dosa", "ghee roast"],
    "idli": ["idli"],
    "sambar": ["sambar"],
    "coconut_chutney": ["coconut chutney", "chutney"],
    "vada": ["medu vada", "vada"],
    "upma": ["upma", "rava upma"],
    "pongal": ["pongal", "ven pongal"],
    "rasam": ["rasam"],
    "curd_rice": ["curd rice", "thayir saadam", "dahi bhaat"],
    "lemon_rice": ["lemon rice", "pulihora", "chitranna"],
    "tamarind_rice": ["tamarind rice", "puliyodharai", "puli sadam"],
    # North Indian
    "chapati": ["chapati", "roti"],
    "naan": ["naan"],
    "dal": ["dal", "lentil"],
    "dal_fry": ["dal fry", "dal tadka"],
    "palak_paneer": ["palak paneer"],
    "paneer_butter_masala": ["paneer butter masala", "paneer makhani"],
    "rajma": ["rajma"],
    "chole": ["chole", "chana masala"],
    # Rice dishes
    "biryani": ["biryani", "biriyani"],
    "mutton_biryani": ["mutton biryani"],
    "chicken_biryani": ["chicken biryani"],
    "veg_biryani": ["vegetable biryani", "veg biryani"],
    "fried_rice": ["fried rice"],
    "plain_rice": ["boiled rice", "plain rice"],
    # Snacks
    "poha": ["poha", "flattened rice", "rice flakes"],
    "bhel_puri": ["bhel puri"],
    "pani_puri": ["pani puri", "golgappa"],
    # Beverages
    "chai": ["hot tea", "garam chai", "tea"],
    "coffee": ["coffee"],
    "lassi": ["lassi"],
    # Generic fallbacks
    "curry": ["curry"],
    "rice": ["boiled rice"],
    "bread": ["chapati", "roti"],
}


@lru_cache(maxsize=1)
def load_indb() -> pd.DataFrame:
    path = Path(settings.indb_file_path)
    if not path.exists():
        # Try relative to backend root
        path = Path(__file__).parent.parent.parent.parent / "data" / "Anuvaad_INDB_2024.11.xlsx"
    df = pd.read_excel(path, engine="openpyxl")
    df["food_name_lower"] = df["food_name"].str.lower().fillna("")
    return df


def find_food_in_indb(food_name: str) -> pd.Series | None:
    df = load_indb()
    name_lower = food_name.lower().replace("_", " ")

    # 1. Try alias map
    aliases = FOOD_ALIASES.get(food_name.lower().replace(" ", "_"), [name_lower])

    for alias in aliases:
        # Exact match
        mask = df["food_name_lower"] == alias
        if mask.any():
            return df[mask].iloc[0]
        # Partial match
        mask = df["food_name_lower"].str.contains(alias, regex=False, na=False)
        if mask.any():
            return df[mask].iloc[0]

    # 2. Word overlap search
    words = [w for w in name_lower.split() if len(w) > 3]
    for word in words:
        mask = df["food_name_lower"].str.contains(word, regex=False, na=False)
        if mask.any():
            return df[mask].iloc[0]

    return None


def _safe_float(val, default=0.0) -> float:
    try:
        f = float(val)
        return f if not np.isnan(f) else default
    except (TypeError, ValueError):
        return default


def calculate_nutrition_from_answers(
    detected_foods: list[str],
    answers: dict[str, str]
) -> dict:
    """
    Main nutrition calculation function.
    Looks up each food in INDB and applies portion/cooking adjustments.
    """
    totals = {
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

    # Parse answers
    portion_mult = 1.0
    cooking_mult = 1.0
    accompaniment_cal = 0.0

    for answer_val in answers.values():
        v = answer_val.lower().strip()
        if v in PORTION_MULTIPLIERS:
            val = PORTION_MULTIPLIERS[v]
            if isinstance(val, float):
                if val <= 3.0 and v in ("half", "one", "two", "more", "more than two",
                                         "half portion", "regular portion (one plate)",
                                         "large portion (two plates)", "small portion (half plate)"):
                    portion_mult = val
                elif v in ("homemade (light oil)", "restaurant", "restaurant (regular)",
                            "restaurant (street food)", "street food/dhaba"):
                    cooking_mult = val
            elif isinstance(val, int):
                accompaniment_cal += val

    for food in detected_foods:
        row = find_food_in_indb(food)
        if row is None:
            # Use generic Indian meal defaults if not found
            totals["total_calories"] += 200 * portion_mult * cooking_mult
            totals["protein_g"] += 6 * portion_mult
            totals["carbs_g"] += 35 * portion_mult
            totals["fat_g"] += 6 * portion_mult * cooking_mult
            totals["fiber_g"] += 2 * portion_mult
            continue

        mult = portion_mult * cooking_mult

        totals["total_calories"] += _safe_float(row.get("energy_kcal")) * mult
        totals["protein_g"] += _safe_float(row.get("protein_g")) * portion_mult
        totals["carbs_g"] += _safe_float(row.get("carb_g")) * portion_mult
        totals["fat_g"] += _safe_float(row.get("fat_g")) * mult
        totals["fiber_g"] += _safe_float(row.get("fibre_g")) * portion_mult
        totals["calcium_mg"] += _safe_float(row.get("calcium_mg")) * portion_mult
        totals["iron_mg"] += _safe_float(row.get("iron_mg")) * portion_mult
        totals["vitamin_c_mg"] += _safe_float(row.get("vitc_mg")) * portion_mult
        totals["potassium_mg"] += _safe_float(row.get("potassium_mg")) * portion_mult
        totals["sodium_mg"] += _safe_float(row.get("sodium_mg")) * portion_mult
        totals["vitamin_a_ug"] += _safe_float(row.get("vita_ug")) * portion_mult

    totals["total_calories"] += accompaniment_cal

    return totals


def compute_health_scores(nutrition: dict) -> dict:
    """Score 0-100 for each health goal."""
    cal = nutrition["total_calories"]
    protein = nutrition["protein_g"]
    carbs = nutrition["carbs_g"]
    fat = nutrition["fat_g"]
    fiber = nutrition["fiber_g"]
    sodium = nutrition["sodium_mg"]

    # Weight loss: lower cal, higher fiber, moderate protein
    wl = 100
    if cal > 600: wl -= min(40, int((cal - 600) / 10))
    if fiber < 3: wl -= 15
    if fat > 30: wl -= 10
    weight_loss = max(0, min(100, wl))

    # Muscle gain: high protein is good
    mg = 50
    mg += min(40, int(protein * 4))
    if cal > 400: mg += 10
    muscle_gain = max(0, min(100, mg))

    # Diabetic friendly: low carbs, low sugar, high fiber
    db = 100
    if carbs > 60: db -= min(50, int((carbs - 60) / 2))
    if fiber >= 4: db += 10
    if fat > 20: db -= 10
    diabetic_friendly = max(0, min(100, db))

    # Heart health: low sodium, low sat fat
    hh = 100
    if sodium > 800: hh -= min(40, int((sodium - 800) / 20))
    if fat > 25: hh -= 15
    if fiber >= 4: hh += 10
    heart_health = max(0, min(100, hh))

    overall = int((weight_loss + muscle_gain + diabetic_friendly + heart_health) / 4)

    return {
        "weight_loss": weight_loss,
        "muscle_gain": muscle_gain,
        "diabetic_friendly": diabetic_friendly,
        "heart_health": heart_health,
        "overall": overall,
    }


def get_food_unit_nutrition(food_name: str) -> dict | None:
    """Return per-unit-serving nutrition data for a food (for live preview)."""
    row = find_food_in_indb(food_name)
    if row is None:
        return None

    def sf(unit_col: str, per100_col: str) -> float:
        v = row.get(unit_col)
        if v is not None and not (isinstance(v, float) and np.isnan(v)) and float(v) != 0:
            return round(float(v), 2)
        v2 = row.get(per100_col)
        return round(_safe_float(v2), 2)

    return {
        "food_name": str(row.get("food_name", food_name)),
        "servings_unit": str(row.get("servings_unit", "per serving")),
        "category": classify_food(food_name),
        "template": TEMPLATES.get(classify_food(food_name), TEMPLATES["GENERAL"]),
        "calories": sf("unit_serving_energy_kcal", "energy_kcal"),
        "protein":  sf("unit_serving_protein_g",   "protein_g"),
        "carbs":    sf("unit_serving_carb_g",       "carb_g"),
        "fat":      sf("unit_serving_fat_g",        "fat_g"),
        "fibre":    sf("unit_serving_fibre_g",      "fibre_g"),
        "calcium":  sf("unit_serving_calcium_mg",   "calcium_mg"),
        "iron":     sf("unit_serving_iron_mg",      "iron_mg"),
        "vitamin_c":sf("unit_serving_vitc_mg",      "vitc_mg"),
        "potassium":sf("unit_serving_potassium_mg", "potassium_mg"),
        "sodium":   sf("unit_serving_sodium_mg",    "sodium_mg"),
    }


def calculate_with_template(food_name: str, answers: dict) -> dict:
    """Calculate nutrition using template multipliers applied to unit_serving values."""
    base = get_food_unit_nutrition(food_name)
    if base is None:
        return {"calories": 200.0, "protein": 6.0, "carbs": 35.0, "fat": 6.0,
                "fibre": 2.0, "calcium": 0.0, "iron": 0.0, "vitamin_c": 0.0,
                "potassium": 0.0, "sodium": 0.0}

    cat = classify_food(food_name)
    template = TEMPLATES.get(cat, TEMPLATES["GENERAL"])

    multiplier = 1.0
    for q in template["questions"]:
        ans = answers.get(q["id"])
        if ans and ans in q["multipliers"]:
            multiplier *= q["multipliers"][ans]

    def m(v: float) -> float:
        return round(v * multiplier, 2)

    return {
        "calories":  m(base["calories"]),
        "protein":   m(base["protein"]),
        "carbs":     m(base["carbs"]),
        "fat":       m(base["fat"]),
        "fibre":     m(base["fibre"]),
        "calcium":   m(base["calcium"]),
        "iron":      m(base["iron"]),
        "vitamin_c": m(base["vitamin_c"]),
        "potassium": m(base["potassium"]),
        "sodium":    m(base["sodium"]),
    }
