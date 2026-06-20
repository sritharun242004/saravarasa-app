"""
Food search & lookup endpoints.

GET /foods/search?q=<query>          → ranked autocomplete list (max 10)
GET /foods/<food_id>                  → single food details + nutrients
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.food_search_service import _food_search_service

router = APIRouter(prefix="/foods", tags=["Foods"])


@router.get("/search")
async def search_foods(
    q: str = Query(..., min_length=1, description="Food search query"),
    db: AsyncSession = Depends(get_db),
):
    """
    Autocomplete food search using PostgreSQL trigram similarity.

    Returns up to 10 results ordered by match confidence.
    Handles spelling mistakes (iddly → Idli, chiken → Chicken).
    Response time target: < 100 ms.
    """
    results = await _food_search_service.search(q.strip(), db, limit=10)
    return results


@router.get("/{food_id}")
async def get_food(food_id: str, db: AsyncSession = Depends(get_db)):
    """Return full nutrient details for a single food (per 100 g)."""
    food = await _food_search_service.get_food(food_id, db)
    if not food:
        raise HTTPException(404, f"Food '{food_id}' not found")
    return food
