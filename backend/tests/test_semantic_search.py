"""
Unit tests for the NutriLens knowledge graph services.
Run: cd backend && python -m pytest tests/ -v
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── Question engine ────────────────────────────────────────────────────────────

from app.services.analysis.question_engine import generate_questions


def test_dosa_questions():
    qs = generate_questions("Masala Dosa", category="Breakfast", region="Karnataka")
    assert len(qs) <= 3
    ids = [q.id for q in qs]
    assert "q_quantity" in ids


def test_biryani_questions():
    qs = generate_questions("Mutton Biryani", category="Rice")
    assert any("biryani" in q.id.lower() or "portion" in q.question.lower() for q in qs)


def test_beverage_questions():
    qs = generate_questions("Hot Tea", category="Beverage")
    assert len(qs) <= 3
    assert any("cup" in q.question.lower() or "large" in " ".join(q.options).lower() for q in qs)


def test_generic_fallback_questions():
    qs = generate_questions("Unknown Dish")
    assert 1 <= len(qs) <= 3


def test_max_3_questions():
    for food in ["Idli", "Pongal", "Curd Rice", "Chapati", "Dal Fry"]:
        qs = generate_questions(food)
        assert len(qs) <= 3, f"Too many questions for {food}: {len(qs)}"


# ── Nutrition engine ───────────────────────────────────────────────────────────

from app.services.nutrition.nutrition_engine import compute_health_scores, _parse_answers


def test_health_scores_range():
    nutrition = {
        "total_calories": 350, "protein_g": 12, "carbs_g": 50,
        "fat_g": 10, "fiber_g": 3, "sodium_mg": 400,
    }
    scores = compute_health_scores(nutrition)
    for key, val in scores.items():
        assert 0 <= val <= 100, f"Score {key}={val} out of range"
    assert "overall" in scores


def test_health_scores_high_cal():
    nutrition = {
        "total_calories": 1200, "protein_g": 5, "carbs_g": 180,
        "fat_g": 45, "fiber_g": 0, "sodium_mg": 2000,
    }
    scores = compute_health_scores(nutrition)
    assert scores["weight_loss"] < 50
    assert scores["heart_health"] < 50


def test_health_scores_healthy_meal():
    nutrition = {
        "total_calories": 250, "protein_g": 20, "carbs_g": 30,
        "fat_g": 5, "fiber_g": 6, "sodium_mg": 200,
    }
    scores = compute_health_scores(nutrition)
    assert scores["muscle_gain"] > 60
    assert scores["diabetic_friendly"] > 60


def test_parse_answers_portion():
    pm, cm, ex = _parse_answers({"q_quantity": "two portions"})
    assert pm == 2.0
    assert cm == 1.0


def test_parse_answers_homemade():
    pm, cm, ex = _parse_answers({"q_prep": "homemade (less oil)"})
    assert cm < 1.0


def test_parse_answers_accompaniment():
    pm, cm, ex = _parse_answers({"q_accomp": "sambar + chutney"})
    assert ex > 0


# ── Embedding text builder ─────────────────────────────────────────────────────

from app.services.embeddings.food_embedding import (
    build_food_embedding_text, infer_category, infer_region, infer_meal_type,
)


def test_build_embedding_text_full():
    text = build_food_embedding_text(
        name="Masala Dosa",
        canonical_name="Masala Dosa",
        category="Breakfast",
        region="Karnataka",
        meal_type="Breakfast",
        ingredients=["rice batter", "potato", "oil"],
        aliases=["masala dose"],
        description="Crispy crepe with potato filling.",
    )
    assert "Masala Dosa" in text
    assert "Karnataka" in text
    assert "potato" in text


def test_infer_category_dosa():
    assert infer_category("masala dosa") == "Breakfast"


def test_infer_category_biryani():
    assert infer_category("mutton biryani") == "Rice"


def test_infer_category_chai():
    assert infer_category("hot tea (garam chai)") == "Beverage"


def test_infer_region_dosa():
    region = infer_region("masala dosa", "Breakfast")
    assert region == "Tamil Nadu"


def test_infer_region_rajma():
    region = infer_region("rajma", "Curry")
    assert region == "Punjab"


def test_infer_meal_type_breakfast():
    assert infer_meal_type("Breakfast", "idli") == "Breakfast"


def test_infer_meal_type_beverage():
    assert infer_meal_type("Beverage", "chai") == "Snack"
