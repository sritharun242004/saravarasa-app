"""
FoodSearchService — PostgreSQL trigram food search.
Pipeline: exact match → alias match → prefix match → trigram similarity.
Target: < 100 ms on a Neon PostgreSQL instance with GIN indexes.
"""
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


# Minimum trigram similarity score to include a result.
_TRGM_THRESHOLD = 0.15


class FoodSearchService:
    async def search(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Return up to *limit* ranked food suggestions for *query*.

        Each result:
            {food_id, food_name, serving_unit, confidence}
        confidence is normalised 0–1.
        """
        q = query.strip().lower()
        if not q:
            return []

        # Single SQL with CTEs — one round-trip, Postgres does the ranking.
        sql = text("""
            WITH
            -- 1. Exact match on canonical name
            exact_name AS (
                SELECT
                    f.id,
                    f.canonical_name,
                    f.serving_unit,
                    1.0::float AS confidence
                FROM foods f
                WHERE LOWER(f.canonical_name) = :q
            ),

            -- 2. Exact match on any alias
            exact_alias AS (
                SELECT
                    f.id,
                    f.canonical_name,
                    f.serving_unit,
                    0.95::float AS confidence
                FROM foods f
                JOIN food_aliases fa ON fa.food_id = f.id
                WHERE LOWER(fa.alias_name) = :q
            ),

            -- 3. Prefix match on canonical name or alias
            prefix_match AS (
                SELECT
                    f.id,
                    f.canonical_name,
                    f.serving_unit,
                    0.80::float AS confidence
                FROM foods f
                WHERE LOWER(f.canonical_name) LIKE :prefix
                UNION ALL
                SELECT
                    f.id,
                    f.canonical_name,
                    f.serving_unit,
                    0.75::float AS confidence
                FROM foods f
                JOIN food_aliases fa ON fa.food_id = f.id
                WHERE LOWER(fa.alias_name) LIKE :prefix
            ),

            -- 4. Trigram similarity on canonical name
            trgm_name AS (
                SELECT
                    f.id,
                    f.canonical_name,
                    f.serving_unit,
                    similarity(LOWER(f.canonical_name), :q) AS confidence
                FROM foods f
                WHERE similarity(LOWER(f.canonical_name), :q) > :threshold
            ),

            -- 5. Trigram similarity on alias names
            trgm_alias AS (
                SELECT
                    f.id,
                    f.canonical_name,
                    f.serving_unit,
                    similarity(LOWER(fa.alias_name), :q) AS confidence
                FROM foods f
                JOIN food_aliases fa ON fa.food_id = f.id
                WHERE similarity(LOWER(fa.alias_name), :q) > :threshold
            ),

            -- Union all tiers
            combined AS (
                SELECT * FROM exact_name
                UNION ALL SELECT * FROM exact_alias
                UNION ALL SELECT * FROM prefix_match
                UNION ALL SELECT * FROM trgm_name
                UNION ALL SELECT * FROM trgm_alias
            ),

            -- Deduplicate by food id, keep highest confidence
            ranked AS (
                SELECT
                    id,
                    canonical_name,
                    serving_unit,
                    MAX(confidence) AS confidence
                FROM combined
                GROUP BY id, canonical_name, serving_unit
            )

            SELECT id, canonical_name, serving_unit, confidence
            FROM ranked
            ORDER BY confidence DESC
            LIMIT :lim
        """)

        result = await db.execute(sql, {
            "q":         q,
            "prefix":    q + "%",
            "threshold": _TRGM_THRESHOLD,
            "lim":       limit,
        })
        rows = result.fetchall()

        return [
            {
                "food_id":     row[0],
                "food_name":   row[1],
                "serving_unit": row[2] or "g",
                "confidence":  round(float(row[3]), 3),
            }
            for row in rows
        ]

    async def get_food(self, food_id: str, db: AsyncSession) -> Dict | None:
        """Fetch a single food by id (for nutrition calculation)."""
        result = await db.execute(
            text("SELECT id, canonical_name, serving_unit, energy_kcal, protein_g, carb_g, fat_g, fiber_g FROM foods WHERE id = :id"),
            {"id": food_id},
        )
        row = result.fetchone()
        if not row:
            return None
        return {
            "food_id":      row[0],
            "food_name":    row[1],
            "serving_unit": row[2] or "g",
            "energy_kcal":  float(row[3] or 0),
            "protein_g":    float(row[4] or 0),
            "carb_g":       float(row[5] or 0),
            "fat_g":        float(row[6] or 0),
            "fiber_g":      float(row[7] or 0),
        }


# ── Unit → gram conversion table ──────────────────────────────────────────────
# Used server-side when computing meal_foods nutrition.
UNIT_GRAM_WEIGHTS: Dict[str, float] = {
    "g":       1.0,
    "100g":    100.0,
    "kg":      1000.0,
    "piece":   50.0,   # sensible default; overridden per-food where known
    "cup":     200.0,
    "bowl":    250.0,
    "plate":   350.0,
    "tbsp":    15.0,
    "tsp":     5.0,
    "serving": 100.0,
    "ml":      1.0,
}

# Per-food piece weights (canonical_name → grams per piece).
# Improves accuracy for common Indian foods.
PIECE_WEIGHTS: Dict[str, float] = {
    "idli":     30.0,
    "dosa":    100.0,
    "uttapam": 120.0,
    "roti":     35.0,
    "chapati":  35.0,
    "phulka":   30.0,
    "paratha":  70.0,
    "puri":     25.0,
    "egg":      50.0,
    "vada":     40.0,
    "bonda":    50.0,
    "samosa":   50.0,
    "pakora":   25.0,
}


def grams_for(quantity: float, unit: str, canonical_name: str = "") -> float:
    """Convert quantity + unit to grams."""
    unit_l = unit.lower().strip()
    if unit_l == "piece":
        per_piece = PIECE_WEIGHTS.get(canonical_name.lower().strip(), 50.0)
        return quantity * per_piece
    return quantity * UNIT_GRAM_WEIGHTS.get(unit_l, 100.0)


def calc_nutrition(
    food: Dict,
    quantity: float,
    unit: str,
) -> Dict[str, float]:
    """Return {calories, protein, carbs, fat} for a given quantity + unit."""
    g = grams_for(quantity, unit, food.get("food_name", ""))
    factor = g / 100.0
    return {
        "calories": round(food["energy_kcal"] * factor, 1),
        "protein":  round(food["protein_g"]   * factor, 1),
        "carbs":    round(food["carb_g"]       * factor, 1),
        "fat":      round(food["fat_g"]        * factor, 1),
    }


_food_search_service = FoodSearchService()
