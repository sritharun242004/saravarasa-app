"""
Analysis v2 routes — Knowledge Graph + Semantic Search architecture.

POST /analysis/image          → Gemini Vision + food detection
POST /analysis/canonicalize   → AI canonical name mapping
POST /analysis/search         → Semantic + alias search
POST /analysis/questions      → Smart question generation
POST /analysis/nutrition      → DB-backed nutrition calculation
GET  /foods/search            → Search food catalogue
GET  /foods/{id}              → Full food node
GET  /foods/{id}/related      → Similar foods
"""
import uuid
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.database import get_db
from app.config import settings
from app.models.meal import Meal, AnalysisSession
from app.models.knowledge_graph import Food

from app.services.gemini.vision import detect_foods
from app.services.search.food_matcher import match_food, canonicalize
from app.services.search.semantic_search import hybrid_search
from app.services.knowledge_graph.graph_service import get_food_node, get_related_foods
from app.services.analysis.question_engine import generate_questions
from app.services.nutrition.nutrition_engine import calculate_nutrition, compute_health_scores
from app.services.recommendations.recommendation_service import get_recommendations
from app.schemas.meal import (
    AnalyzeImageResponse, DetectedFood,
    NutritionResult, Micronutrients, HealthScores,
    MealHistory, MealSummary,
)

router = APIRouter(prefix="/analysis", tags=["Analysis v2"])
food_router = APIRouter(prefix="/foods", tags=["Foods"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}


# ── POST /analysis/image ──────────────────────────────────────────────────────

@router.post("/image")
async def analyze_image_v2(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Unsupported image type.")

    contents = await file.read()
    if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {settings.max_upload_size_mb}MB limit.")

    # Save image
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    async with aiofiles.open(upload_path / filename, "wb") as f:
        await f.write(contents)
    image_url = f"/uploads/{filename}"

    # Gemini Vision detection
    detection = await detect_foods(contents)
    raw_foods = detection.get("foods", [])
    if not raw_foods:
        raw_foods = [{"name": "unknown_dish", "display_name": "Indian Dish", "confidence": 0.5}]

    # Semantic match each detected food against the knowledge graph
    matched = []
    food_ids: list[str] = []
    for raw in raw_foods[:3]:
        food_match = await match_food(raw.get("display_name", raw["name"]), db)
        entry = {
            "name": raw["name"],
            "display_name": raw.get("display_name", raw["name"]),
            "confidence": float(raw.get("confidence", 0.5)),
            "canonical_name": food_match.canonical_name,
            "food_id": food_match.best.food.id if food_match.best else None,
            "graph_score": food_match.best.score if food_match.best else 0.0,
        }
        matched.append(entry)
        if food_match.best:
            food_ids.append(food_match.best.food.id)

    # Create session
    session_id = str(uuid.uuid4())
    session = AnalysisSession(
        id=session_id,
        image_url=image_url,
        detected_foods=matched,
        status="detected",
    )
    db.add(session)
    await db.commit()

    return {
        "session_id": session_id,
        "image_url": image_url,
        "foods": matched,
        "food_ids": food_ids,
    }


# ── POST /analysis/canonicalize ───────────────────────────────────────────────

@router.post("/canonicalize")
async def canonicalize_food(body: dict):
    """Map any raw food detection string to a canonical Indian dish name."""
    raw = body.get("food_name", "")
    result = await canonicalize(raw)
    return result


# ── POST /analysis/search ─────────────────────────────────────────────────────

@router.post("/search")
async def search_foods(body: dict, db: AsyncSession = Depends(get_db)):
    """
    Semantic + alias search. Returns ranked food matches with scores.
    """
    query = body.get("query", "").strip()
    limit = int(body.get("limit", 5))
    if not query:
        raise HTTPException(400, "query is required")

    results = await hybrid_search(query, db, limit=limit)
    return {"query": query, "results": [r.to_dict() for r in results]}


# ── POST /analysis/questions ──────────────────────────────────────────────────

@router.post("/questions")
async def get_questions(body: dict, db: AsyncSession = Depends(get_db)):
    """
    Generate smart follow-up questions for a detected food.
    """
    session_id = body.get("session_id", "")
    foods = body.get("foods", [])     # list of food names
    food_ids = body.get("food_ids", [])

    all_questions = []
    for i, food_name in enumerate(foods[:2]):  # max 2 foods to keep ≤3 questions total
        # Get category from graph if we have food_id
        category = None
        region = None
        if i < len(food_ids) and food_ids[i]:
            node = await get_food_node(food_ids[i], db)
            if node:
                category = node.get("category")
                region = node.get("region")

        qs = generate_questions(food_name, category=category, region=region)
        all_questions.extend(qs)

    # Deduplicate by id and cap at 3
    seen_ids: set[str] = set()
    final: list[dict] = []
    for q in all_questions:
        if q.id not in seen_ids:
            seen_ids.add(q.id)
            final.append({
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "food_name": q.food_name,
            })
        if len(final) >= 3:
            break

    # Update session
    if session_id:
        session = await db.get(AnalysisSession, session_id)
        if session:
            session.questions = final
            session.status = "questions_generated"
            await db.commit()

    return {"questions": final, "session_id": session_id}


# ── POST /analysis/nutrition ──────────────────────────────────────────────────

@router.post("/nutrition")
async def calculate_nutrition_v2(body: dict, db: AsyncSession = Depends(get_db)):
    """
    Calculate nutrition from graph DB using food_ids + user answers.
    """
    session_id = body.get("session_id", "")
    food_ids: list[str] = body.get("food_ids", [])
    answers: dict[str, str] = body.get("answers", {})

    if not food_ids:
        # Try to get food_ids from session
        if session_id:
            session = await db.get(AnalysisSession, session_id)
            if session and session.detected_foods:
                food_ids = [f["food_id"] for f in session.detected_foods if f.get("food_id")]

    if not food_ids:
        raise HTTPException(400, "No food_ids provided or found in session.")

    session = await db.get(AnalysisSession, session_id) if session_id else None
    image_url = session.image_url if session else None

    # Nutrition from DB
    nutrition = await calculate_nutrition(food_ids, answers, db)
    scores = compute_health_scores(nutrition)

    # Food display names
    food_names: list[str] = []
    for fid in food_ids:
        node = await get_food_node(fid, db)
        if node:
            food_names.append(node["canonical_name"])

    # Save meal
    meal = Meal(
        session_id=session_id or str(uuid.uuid4()),
        image_url=image_url,
        detected_foods=food_names,
        total_calories=nutrition["total_calories"],
        protein_g=nutrition["protein_g"],
        carbs_g=nutrition["carbs_g"],
        fat_g=nutrition["fat_g"],
        fiber_g=nutrition["fiber_g"],
        micronutrients={
            "calcium_mg": nutrition["calcium_mg"],
            "iron_mg": nutrition["iron_mg"],
            "vitamin_c_mg": nutrition["vitamin_c_mg"],
            "potassium_mg": nutrition["potassium_mg"],
            "sodium_mg": nutrition["sodium_mg"],
            "vitamin_a_ug": nutrition["vitamin_a_ug"],
        },
        health_scores=scores,
        question_answers=answers,
    )
    db.add(meal)
    if session:
        session.status = "completed"
    await db.commit()
    await db.refresh(meal)

    return NutritionResult(
        meal_id=meal.id,
        foods=food_names,
        total_calories=meal.total_calories,
        protein_g=meal.protein_g,
        carbs_g=meal.carbs_g,
        fat_g=meal.fat_g,
        fiber_g=meal.fiber_g,
        micronutrients=Micronutrients(**meal.micronutrients),
        health_scores=HealthScores(**meal.health_scores),
        image_url=meal.image_url,
        created_at=meal.created_at.isoformat(),
    )


# ── GET /foods/search ─────────────────────────────────────────────────────────

@food_router.get("/search")
async def search_food_catalogue(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    results = await hybrid_search(q, db, limit=limit)
    return {"results": [r.to_dict() for r in results]}


# ── GET /foods/{food_id} ──────────────────────────────────────────────────────

@food_router.get("/{food_id}")
async def get_food(food_id: str, db: AsyncSession = Depends(get_db)):
    node = await get_food_node(food_id, db)
    if not node:
        raise HTTPException(404, "Food not found")
    return node


# ── GET /foods/{food_id}/related ──────────────────────────────────────────────

@food_router.get("/{food_id}/related")
async def get_related(
    food_id: str,
    limit: int = Query(5, le=20),
    goal: str = Query("weight_loss"),
    db: AsyncSession = Depends(get_db),
):
    related = await get_related_foods(food_id, db, limit=limit)
    recommendations = await get_recommendations(food_id, db, goal=goal, limit=limit)
    return {
        "related_foods": related,
        "recommendations": recommendations,
        "goal": goal,
    }
