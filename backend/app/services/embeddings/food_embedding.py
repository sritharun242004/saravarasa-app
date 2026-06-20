"""
Builds rich text representations of food items for high-quality embeddings.
The richer the text, the better the semantic matching.
"""
from typing import Optional


def build_food_embedding_text(
    name: str,
    canonical_name: str,
    category: Optional[str] = None,
    region: Optional[str] = None,
    meal_type: Optional[str] = None,
    ingredients: Optional[list[str]] = None,
    aliases: Optional[list[str]] = None,
    description: Optional[str] = None,
) -> str:
    """
    Compose a rich natural-language description used as input to the embedding model.
    Format is designed to maximise semantic recall for Indian cuisine queries.
    """
    parts: list[str] = []

    parts.append(canonical_name)

    if aliases:
        parts.append(f"Also known as: {', '.join(aliases[:6])}.")

    if category:
        parts.append(f"Category: {category}.")

    if region:
        parts.append(f"Region: {region} cuisine.")

    if meal_type:
        parts.append(f"Typically eaten as {meal_type.lower()}.")

    if ingredients:
        parts.append(f"Key ingredients: {', '.join(ingredients[:8])}.")

    if description:
        parts.append(description)

    return " ".join(parts)


# ── Static alias + ingredient knowledge base ──────────────────────────────────
# Used by import_indb.py to enrich foods that don't have explicit metadata.

FOOD_KNOWLEDGE: dict[str, dict] = {
    "masala dosa": {
        "aliases": ["masala dose", "masala dosai", "paper roast", "mysore masala dosa"],
        "category": "Breakfast",
        "region": "Karnataka",
        "meal_type": "Breakfast",
        "ingredients": ["rice batter", "urad dal", "potato", "onion", "mustard seeds", "oil"],
        "description": "Crispy rice crepe stuffed with spiced potato filling, served with sambar and coconut chutney.",
    },
    "plain dosa": {
        "aliases": ["sada dosa", "plain dose", "dosa"],
        "category": "Breakfast",
        "region": "South India",
        "meal_type": "Breakfast",
        "ingredients": ["rice batter", "urad dal", "oil"],
        "description": "Thin crispy fermented rice and lentil crepe.",
    },
    "semolina dosa": {
        "aliases": ["rava dosa", "suji dosa", "rava dose", "instant dosa"],
        "category": "Breakfast",
        "region": "South India",
        "meal_type": "Breakfast",
        "ingredients": ["semolina", "rice flour", "maida", "onion", "green chilli", "oil"],
        "description": "Crispy lacy dosa made from semolina batter.",
    },
    "idli": {
        "aliases": ["idly", "steamed idli", "rice idli"],
        "category": "Breakfast",
        "region": "Tamil Nadu",
        "meal_type": "Breakfast",
        "ingredients": ["rice", "urad dal"],
        "description": "Soft steamed fermented rice and lentil cakes.",
    },
    "sambar": {
        "aliases": ["sambhar", "vegetable sambar", "drumstick sambar"],
        "category": "Curry",
        "region": "Tamil Nadu",
        "meal_type": "Lunch",
        "ingredients": ["toor dal", "tamarind", "tomato", "drumstick", "sambar powder"],
        "description": "South Indian lentil vegetable stew with tamarind base.",
    },
    "pongal": {
        "aliases": ["ven pongal", "khichdi pongal", "rice pongal"],
        "category": "Breakfast",
        "region": "Tamil Nadu",
        "meal_type": "Breakfast",
        "ingredients": ["rice", "moong dal", "ghee", "pepper", "cumin", "cashew"],
        "description": "Creamy rice and lentil porridge seasoned with pepper and ghee.",
    },
    "upma": {
        "aliases": ["rava upma", "semolina upma", "suji upma"],
        "category": "Breakfast",
        "region": "South India",
        "meal_type": "Breakfast",
        "ingredients": ["semolina", "onion", "mustard seeds", "curry leaves", "oil"],
        "description": "Savory semolina porridge with vegetables and spices.",
    },
    "curd rice": {
        "aliases": ["thayir saadam", "dahi chawal", "dahi bhaat", "daddojanam", "perugu annam"],
        "category": "Rice",
        "region": "Tamil Nadu",
        "meal_type": "Lunch",
        "ingredients": ["rice", "curd", "mustard seeds", "curry leaves", "ginger"],
        "description": "Comforting south Indian rice mixed with yogurt and tempered spices.",
    },
    "lemon rice": {
        "aliases": ["pulihora", "elumichai sadam", "chitranna", "nimbu chawal"],
        "category": "Rice",
        "region": "Andhra Pradesh",
        "meal_type": "Lunch",
        "ingredients": ["rice", "lemon juice", "turmeric", "mustard seeds", "peanuts", "curry leaves"],
        "description": "Tangy rice dish flavored with lemon juice and tempered spices.",
    },
    "tamarind rice": {
        "aliases": ["puliyodharai", "puli sadam", "chintapandu pulihora", "huli anna"],
        "category": "Rice",
        "region": "Tamil Nadu",
        "meal_type": "Lunch",
        "ingredients": ["rice", "tamarind", "sesame seeds", "peanuts", "chilli", "jaggery"],
        "description": "Tangy spicy rice made with tamarind paste and spice mix.",
    },
    "chapati": {
        "aliases": ["roti", "phulka", "wheat roti", "whole wheat chapati"],
        "category": "Bread",
        "region": "North India",
        "meal_type": "Lunch",
        "ingredients": ["whole wheat flour", "water", "oil"],
        "description": "Thin unleavened whole wheat flatbread cooked on a tawa.",
    },
    "mutton biryani": {
        "aliases": ["gosht biryani", "lamb biryani", "mutton biriyani"],
        "category": "Rice",
        "region": "Hyderabad",
        "meal_type": "Lunch",
        "ingredients": ["basmati rice", "mutton", "yogurt", "onion", "biryani masala", "saffron", "ghee"],
        "description": "Aromatic slow-cooked layered rice dish with mutton.",
    },
    "vegetable biryani": {
        "aliases": ["veg biryani", "vegetarian biryani", "veg biriyani"],
        "category": "Rice",
        "region": "Hyderabad",
        "meal_type": "Lunch",
        "ingredients": ["basmati rice", "mixed vegetables", "yogurt", "biryani masala", "ghee"],
        "description": "Fragrant layered rice with mixed vegetables and whole spices.",
    },
    "hot tea": {
        "aliases": ["garam chai", "chai", "masala chai", "indian tea", "milk tea"],
        "category": "Beverage",
        "region": "All India",
        "meal_type": "Snack",
        "ingredients": ["tea leaves", "milk", "sugar", "ginger", "cardamom"],
        "description": "Spiced Indian milk tea boiled with ginger and cardamom.",
    },
    "boiled rice": {
        "aliases": ["plain rice", "steamed rice", "white rice", "cooked rice", "uble chawal"],
        "category": "Rice",
        "region": "All India",
        "meal_type": "Lunch",
        "ingredients": ["rice", "water"],
        "description": "Plain steamed white rice.",
    },
    "dal parantha": {
        "aliases": ["dal paratha", "lentil paratha", "stuffed paratha"],
        "category": "Bread",
        "region": "Punjab",
        "meal_type": "Breakfast",
        "ingredients": ["whole wheat flour", "chana dal", "spices", "ghee"],
        "description": "Whole wheat flatbread stuffed with spiced lentil filling.",
    },
    "medu vada": {
        "aliases": ["vada", "urad dal vada", "ulundu vadai", "medhu vadai"],
        "category": "Snack",
        "region": "South India",
        "meal_type": "Breakfast",
        "ingredients": ["urad dal", "onion", "curry leaves", "green chilli", "oil"],
        "description": "Crispy savory fried doughnut made from urad dal.",
    },
    "rasam": {
        "aliases": ["pepper rasam", "tomato rasam", "charu", "saaru"],
        "category": "Curry",
        "region": "Tamil Nadu",
        "meal_type": "Lunch",
        "ingredients": ["tamarind", "tomato", "pepper", "cumin", "curry leaves", "asafoetida"],
        "description": "Thin spicy South Indian soup served with rice.",
    },
    "poha": {
        "aliases": ["aval", "flattened rice", "chiwda", "rice flakes poha"],
        "category": "Breakfast",
        "region": "Maharashtra",
        "meal_type": "Breakfast",
        "ingredients": ["flattened rice", "onion", "mustard seeds", "turmeric", "peanuts", "lemon"],
        "description": "Light breakfast made from flattened rice with onion and spices.",
    },
    "palak paneer": {
        "aliases": ["spinach paneer", "saag paneer", "palak cottage cheese"],
        "category": "Curry",
        "region": "North India",
        "meal_type": "Lunch",
        "ingredients": ["spinach", "paneer", "onion", "tomato", "cream", "garam masala"],
        "description": "Creamy spinach curry with soft Indian cottage cheese cubes.",
    },
    "dal fry": {
        "aliases": ["dal tadka", "tempered dal", "yellow dal fry", "toor dal fry"],
        "category": "Curry",
        "region": "North India",
        "meal_type": "Lunch",
        "ingredients": ["toor dal", "onion", "tomato", "cumin", "garlic", "ghee"],
        "description": "Slow-cooked lentils tempered with aromatic spices in ghee.",
    },
}


def get_food_knowledge(food_name_lower: str) -> dict:
    """Return enrichment data for a known food, or empty dict."""
    return FOOD_KNOWLEDGE.get(food_name_lower, {})


def infer_category(food_name_lower: str) -> str:
    """Rule-based category inference from food name keywords."""
    name = food_name_lower
    if any(k in name for k in ["dosa", "idli", "upma", "pongal", "poha", "paratha", "parantha",
                                 "vada", "vadai", "pesarattu", "uttapam", "appam"]):
        return "Breakfast"
    if any(k in name for k in ["biryani", "biriyani", "rice", "chawal", "sadam", "annam"]):
        return "Rice"
    if any(k in name for k in ["chapati", "roti", "naan", "paratha", "bread", "poori", "puri",
                                 "kulcha", "bhatura"]):
        return "Bread"
    if any(k in name for k in ["chai", "tea", "coffee", "juice", "lassi", "buttermilk",
                                 "sherbet", "sharbat", "drink", "beverage", "kanji"]):
        return "Beverage"
    if any(k in name for k in ["halwa", "kheer", "payasam", "ladoo", "barfi", "gulab",
                                 "jalebi", "rasgulla", "sweet", "pudding", "dessert"]):
        return "Sweet"
    if any(k in name for k in ["sambar", "rasam", "dal", "curry", "gravy", "masala",
                                 "paneer", "chicken", "mutton", "fish", "sabzi", "palak",
                                 "rajma", "chole", "chana"]):
        return "Curry"
    if any(k in name for k in ["bhel", "chaat", "pani puri", "vada pav", "pakora",
                                 "bajji", "bonda", "murukku", "chips", "snack", "mixture"]):
        return "Snack"
    if any(k in name for k in ["salad", "raita", "chutney", "pickle", "papad",
                                 "achar", "kosambari"]):
        return "Condiment"
    return "Other"


def infer_region(food_name_lower: str, category: str) -> str:
    """Rule-based region inference."""
    name = food_name_lower
    if any(k in name for k in ["dosa", "idli", "sambar", "rasam", "pongal", "dosai",
                                 "vadai", "uttapam", "kozhukattai", "appam", "puttu",
                                 "thayir", "sadam"]):
        return "Tamil Nadu"
    if any(k in name for k in ["pulihora", "pesarattu", "gongura", "andhra"]):
        return "Andhra Pradesh"
    if any(k in name for k in ["bisi bele", "chitranna", "ragi mudde", "Karnataka", "obbattu"]):
        return "Karnataka"
    if any(k in name for k in ["appam", "puttu", "avial", "olan", "Kerala", "payasam"]):
        return "Kerala"
    if any(k in name for k in ["biryani", "haleem", "hyderabad"]):
        return "Hyderabad"
    if any(k in name for k in ["rajma", "chole", "sarson", "makki", "lassi", "Punjab",
                                 "naan", "tandoor", "butter chicken"]):
        return "Punjab"
    if any(k in name for k in ["dal baati", "laal maas", "rajasthan"]):
        return "Rajasthan"
    if any(k in name for k in ["vada pav", "misal", "pav bhaji", "Maharashtra", "puran poli"]):
        return "Maharashtra"
    if any(k in name for k in ["dhokla", "thepla", "Gujarat", "khakhra", "undhiyu"]):
        return "Gujarat"
    return "All India"


def infer_meal_type(category: str, food_name_lower: str) -> str:
    name = food_name_lower
    if category == "Breakfast":
        return "Breakfast"
    if category == "Beverage":
        return "Snack"
    if category == "Sweet":
        return "Dessert"
    if category == "Snack":
        return "Snack"
    if any(k in name for k in ["dinner", "night"]):
        return "Dinner"
    return "Lunch"
