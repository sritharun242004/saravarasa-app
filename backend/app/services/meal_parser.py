"""
Parse free-text meal submissions into structured food + quantity lists.

Examples:
    "3 idli, sambar, tea"         → [{qty:3, name:"idli"}, {qty:1, name:"sambar"}, ...]
    "2 boiled egg\nrice\n1 cup dal" → [{qty:2, name:"boiled egg"}, ...]
"""
import re
from typing import List, Dict

_NUMBER_WORDS = {
    "half": 0.5, "quarter": 0.25,
    "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
    "a": 1.0, "an": 1.0,
}

# Units that precede food names and should be stripped
_UNIT_PATTERN = r"(?:cup|plate|bowl|piece|pcs|nos|no|katori|glass|serving)s?\b\.?"

# Descriptors that don't affect nutrition lookup
_NOISE_WORDS = r"\b(hot|cold|fresh|boiled|fried|plain|steamed|raw|cooked|sweet|spicy)\b"


def parse_meal_text(text: str) -> List[Dict]:
    items = []

    # Split on commas, newlines, semicolons, plus signs
    parts = re.split(r"[,\n;+]+", text)

    for part in parts:
        part = part.strip().lower()
        if not part:
            continue

        # Match leading numeric quantity (int, decimal, or fraction like "1/2")
        m = re.match(
            rf"^(\d+(?:\.\d+)?(?:/\d+)?)\s*{_UNIT_PATTERN}?\s*(.+)",
            part,
        )
        if m:
            qty_str, name = m.group(1), m.group(2).strip()
            qty = _parse_qty(qty_str)
        else:
            # Try number words at the start
            qty = 1.0
            name = part
            for word, val in _NUMBER_WORDS.items():
                if re.match(rf"^{re.escape(word)}\s+", part):
                    qty = val
                    name = re.sub(rf"^{re.escape(word)}\s+", "", part).strip()
                    break

        # Strip noise descriptors and extra whitespace
        name = re.sub(_NOISE_WORDS, "", name)
        name = re.sub(r"\s+", " ", name).strip()

        if name and len(name) > 1:
            items.append({"quantity": qty, "food_name": name})

    return items


def _parse_qty(qty_str: str) -> float:
    if "/" in qty_str:
        num, den = qty_str.split("/", 1)
        return float(num) / float(den)
    return float(qty_str)
