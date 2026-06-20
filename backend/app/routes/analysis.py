import os
import uuid
import aiofiles
import pandas as pd
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models.meal import Meal, AnalysisSession
from app.schemas.meal import (
    AnalyzeImageResponse, DetectedFood,
    GenerateQuestionsRequest, QuestionsResponse, Question,
    CalculateNutritionRequest, NutritionResult,
    MealHistory, MealSummary, Micronutrients, HealthScores,
    DashboardData, DailyData, TopFood,
    ManualAnalyzeRequest, ManualAnalyzeResponse, FoodMatch,
)
from app.services.gemini.vision import detect_foods, generate_questions_ai
from app.services.nutrition.indb_engine import (
    calculate_nutrition_from_answers, compute_health_scores,
    find_food_in_indb, load_indb,
    get_food_unit_nutrition, calculate_with_template, classify_food, TEMPLATES,
)
from app.config import settings

router = APIRouter()
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}


@router.post("/analyze-image", response_model=AnalyzeImageResponse)
async def analyze_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Unsupported image type. Use JPG, PNG, or WEBP.")

    contents = await file.read()
    if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(400, f"File too large. Max {settings.max_upload_size_mb}MB.")

    # Save image
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    file_path = upload_path / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    image_url = f"/uploads/{filename}"

    # Detect foods via Gemini
    detection = await detect_foods(contents)
    foods = detection.get("foods", [])

    if not foods:
        foods = [{"name": "unknown_dish", "display_name": "Indian Dish", "confidence": 0.5}]

    # Create session
    session_id = str(uuid.uuid4())
    session = AnalysisSession(
        id=session_id,
        image_url=image_url,
        detected_foods=foods,
        status="detected",
    )
    db.add(session)
    await db.commit()

    return AnalyzeImageResponse(
        foods=[DetectedFood(**f) for f in foods],
        image_url=image_url,
        session_id=session_id,
    )


@router.post("/generate-questions", response_model=QuestionsResponse)
async def generate_questions(
    req: GenerateQuestionsRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await generate_questions_ai(req.foods)
    questions_data = result.get("questions", [])

    questions = [Question(**q) for q in questions_data]

    # Update session
    session = await db.get(AnalysisSession, req.session_id)
    if session:
        session.questions = [q.model_dump() for q in questions]
        session.status = "questions_generated"
        await db.commit()

    return QuestionsResponse(questions=questions, session_id=req.session_id)


@router.post("/calculate-nutrition", response_model=NutritionResult)
async def calculate_nutrition(
    req: CalculateNutritionRequest,
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(AnalysisSession, req.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    detected = session.detected_foods or []
    food_names = [f.get("name", "unknown") for f in detected]
    display_names = [f.get("display_name", f.get("name", "Dish")) for f in detected]

    # Calculate nutrition from INDB
    nutrition = calculate_nutrition_from_answers(food_names, req.answers)
    scores = compute_health_scores(nutrition)

    # Save meal
    meal = Meal(
        session_id=req.session_id,
        image_url=session.image_url,
        detected_foods=display_names,
        total_calories=round(nutrition["total_calories"], 2),
        protein_g=round(nutrition["protein_g"], 2),
        carbs_g=round(nutrition["carbs_g"], 2),
        fat_g=round(nutrition["fat_g"], 2),
        fiber_g=round(nutrition["fiber_g"], 2),
        micronutrients={
            "calcium_mg": round(nutrition["calcium_mg"], 2),
            "iron_mg": round(nutrition["iron_mg"], 2),
            "vitamin_c_mg": round(nutrition["vitamin_c_mg"], 2),
            "potassium_mg": round(nutrition["potassium_mg"], 2),
            "sodium_mg": round(nutrition["sodium_mg"], 2),
            "vitamin_a_ug": round(nutrition["vitamin_a_ug"], 2),
        },
        health_scores=scores,
        question_answers=req.answers,
    )
    db.add(meal)
    session.status = "completed"
    await db.commit()
    await db.refresh(meal)

    return NutritionResult(
        meal_id=meal.id,
        foods=display_names,
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


@router.post("/manual-session", response_model=ManualAnalyzeResponse)
async def manual_session(
    req: ManualAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    cleaned = [n.strip() for n in req.food_names if n.strip()]
    if not cleaned:
        raise HTTPException(400, "Provide at least one food name.")

    foods = []
    matches = []
    for food_name in cleaned:
        row = find_food_in_indb(food_name)
        if row is not None:
            indb_name = str(row.get("food_name", food_name))
            foods.append({
                "name": food_name.lower().replace(" ", "_"),
                "display_name": indb_name,
                "confidence": 1.0,
            })
            matches.append(FoodMatch(input_name=food_name, matched=True, indb_name=indb_name))
        else:
            foods.append({
                "name": food_name.lower().replace(" ", "_"),
                "display_name": food_name.title(),
                "confidence": 0.5,
            })
            matches.append(FoodMatch(input_name=food_name, matched=False, indb_name=None))

    session_id = str(uuid.uuid4())
    session = AnalysisSession(
        id=session_id,
        image_url=None,
        detected_foods=foods,
        status="detected",
    )
    db.add(session)
    await db.commit()

    return ManualAnalyzeResponse(
        foods=[DetectedFood(**f) for f in foods],
        image_url="",
        session_id=session_id,
        matches=matches,
    )


_SEARCH_SYNONYMS: dict[str, list[str]] = {
    "chai":    ["chai", "tea"],
    "tea":     ["tea", "chai", "garam"],
    "kaapi":   ["coffee", "kaapi"],
    "coffee":  ["coffee", "kaapi"],
    "dosa":    ["dosa", "dosai"],
    "dosai":   ["dosa", "dosai"],
    "idly":    ["idli", "idly"],
    "idli":    ["idli", "idly"],
    "dal":     ["dal", "dhal", "lentil"],
    "dhal":    ["dal", "dhal"],
    "daal":    ["dal", "dhal"],
    "roti":    ["roti", "chapati", "chapathi"],
    "chapati": ["chapati", "chapathi", "roti"],
    "chapathi":["chapathi", "chapati", "roti"],
    "biryani": ["biryani", "biriyani"],
    "biriyani":["biriyani", "biryani"],
    "sambar":  ["sambar", "sambhar"],
    "sambhar": ["sambar", "sambhar"],
    "vada":    ["vada", "vadai", "medu"],
    "vadai":   ["vadai", "vada", "medu"],
    "medu":    ["medu", "vada", "vadai"],
    "poha":    ["poha", "flattened rice"],
    "upma":    ["upma", "rava"],
    "lassi":   ["lassi", "buttermilk"],
    "curd":    ["curd", "dahi", "yoghurt", "yogurt"],
    "dahi":    ["dahi", "curd", "yoghurt"],
    "paneer":  ["paneer", "cottage cheese"],
    "puri":    ["puri", "poori"],
    "poori":   ["poori", "puri"],
    "khichdi": ["khichdi", "khichri"],
    "paratha": ["paratha", "parantha"],
    "halwa":   ["halwa", "halva"],
    "ladoo":   ["ladoo", "laddoo"],
    "payasam": ["payasam", "kheer"],
    "kheer":   ["kheer", "payasam"],
    "rasam":   ["rasam"],
    "pongal":  ["pongal", "ven pongal"],
}


@router.get("/foods/autocomplete")
async def autocomplete_foods(q: str = ""):
    if len(q) < 2:
        return {"suggestions": []}
    df = load_indb()
    q_lower = q.lower().strip()

    # Expand query with synonyms for related-word matching
    search_terms = list({q_lower} | set(_SEARCH_SYNONYMS.get(q_lower, [])))

    mask = pd.Series([False] * len(df), index=df.index)
    for term in search_terms:
        mask = mask | df["food_name_lower"].str.contains(term, regex=False, na=False)

    suggestions = df[mask]["food_name"].head(20).tolist()
    return {"suggestions": suggestions}


@router.get("/meals/{meal_id}", response_model=NutritionResult)
async def get_meal(meal_id: str, db: AsyncSession = Depends(get_db)):
    meal = await db.get(Meal, meal_id)
    if not meal:
        raise HTTPException(404, "Meal not found")

    return NutritionResult(
        meal_id=meal.id,
        foods=meal.detected_foods or [],
        total_calories=meal.total_calories,
        protein_g=meal.protein_g,
        carbs_g=meal.carbs_g,
        fat_g=meal.fat_g,
        fiber_g=meal.fiber_g,
        micronutrients=Micronutrients(**(meal.micronutrients or {})),
        health_scores=HealthScores(**(meal.health_scores or {})),
        image_url=meal.image_url,
        created_at=meal.created_at.isoformat(),
    )


@router.get("/meal-history", response_model=MealHistory)
async def get_meal_history(
    page: int = 1,
    limit: int = 10,
    search: str = "",
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    query = select(Meal).order_by(desc(Meal.created_at))

    if search:
        query = query.where(
            Meal.detected_foods.cast(str).ilike(f"%{search}%")
        )

    total_q = select(func.count()).select_from(query.subquery())
    total = await db.scalar(total_q) or 0

    meals = (await db.execute(query.offset(offset).limit(limit))).scalars().all()

    return MealHistory(
        meals=[
            MealSummary(
                meal_id=m.id,
                foods=m.detected_foods or [],
                total_calories=m.total_calories,
                protein_g=m.protein_g,
                image_url=m.image_url,
                created_at=m.created_at.isoformat(),
            )
            for m in meals
        ],
        total=total,
    )


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=6)

    # Today's totals
    today_q = select(
        func.coalesce(func.sum(Meal.total_calories), 0),
        func.coalesce(func.sum(Meal.protein_g), 0),
        func.coalesce(func.sum(Meal.carbs_g), 0),
        func.coalesce(func.sum(Meal.fat_g), 0),
    ).where(func.date(Meal.created_at) == today)

    today_row = (await db.execute(today_q)).one()

    # Weekly data
    weekly_q = select(
        func.date(Meal.created_at).label("date"),
        func.sum(Meal.total_calories).label("calories"),
        func.sum(Meal.protein_g).label("protein"),
    ).where(
        func.date(Meal.created_at) >= week_ago
    ).group_by(func.date(Meal.created_at)).order_by("date")

    weekly_rows = (await db.execute(weekly_q)).all()

    # Fill missing days
    weekly_map = {str(r.date): r for r in weekly_rows}
    weekly_data = []
    for i in range(7):
        d = str(week_ago + timedelta(days=i))
        row = weekly_map.get(d)
        weekly_data.append(DailyData(
            date=d[5:],  # MM-DD
            calories=round(float(row.calories), 1) if row else 0,
            protein=round(float(row.protein), 1) if row else 0,
        ))

    # Top foods this week
    all_meals = (await db.execute(
        select(Meal.detected_foods).where(func.date(Meal.created_at) >= week_ago)
    )).scalars().all()

    food_counts: dict = {}
    for foods in all_meals:
        for f in (foods or []):
            food_counts[f] = food_counts.get(f, 0) + 1

    top_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return DashboardData(
        today_calories=round(float(today_row[0]), 1),
        today_protein=round(float(today_row[1]), 1),
        today_carbs=round(float(today_row[2]), 1),
        today_fat=round(float(today_row[3]), 1),
        calorie_goal=2000,
        weekly_data=weekly_data,
        top_foods=[TopFood(name=n, count=c) for n, c in top_foods],
    )


# ── New template-based endpoints ──────────────────────────────────────────────

@router.get("/foods/nutrition")
async def get_food_nutrition(name: str):
    """Return unit-serving nutrition + template questions for a food (live preview)."""
    data = get_food_unit_nutrition(name)
    if data is None:
        cat = classify_food(name)
        data = {
            "food_name": name,
            "servings_unit": "per serving",
            "category": cat,
            "template": TEMPLATES.get(cat, TEMPLATES["GENERAL"]),
            "calories": 150.0, "protein": 5.0, "carbs": 25.0, "fat": 4.0,
            "fibre": 1.5, "calcium": 0.0, "iron": 0.0, "vitamin_c": 0.0,
            "potassium": 0.0, "sodium": 0.0,
        }
    return data


class _MealItemIn(BaseModel):
    food_name: str
    category: str
    answers: Dict[str, str]


class ManualCompleteRequest(BaseModel):
    meal_type: str = "general"
    items: List[_MealItemIn]


@router.post("/manual-analyze-complete", response_model=NutritionResult)
async def manual_analyze_complete(
    req: ManualCompleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """One-shot endpoint: accepts meal cart with template answers, returns NutritionResult."""
    if not req.items:
        raise HTTPException(400, "Provide at least one food item.")

    totals = {
        "total_calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0,
        "fat_g": 0.0, "fiber_g": 0.0, "calcium_mg": 0.0, "iron_mg": 0.0,
        "vitamin_c_mg": 0.0, "potassium_mg": 0.0, "sodium_mg": 0.0, "vitamin_a_ug": 0.0,
    }
    display_names = []

    for item in req.items:
        nut = calculate_with_template(item.food_name, item.answers)
        row = find_food_in_indb(item.food_name)
        dn = str(row.get("food_name", item.food_name)) if row is not None else item.food_name.title()
        display_names.append(dn)
        totals["total_calories"] += nut["calories"]
        totals["protein_g"]      += nut["protein"]
        totals["carbs_g"]        += nut["carbs"]
        totals["fat_g"]          += nut["fat"]
        totals["fiber_g"]        += nut["fibre"]
        totals["calcium_mg"]     += nut["calcium"]
        totals["iron_mg"]        += nut["iron"]
        totals["vitamin_c_mg"]   += nut["vitamin_c"]
        totals["potassium_mg"]   += nut["potassium"]
        totals["sodium_mg"]      += nut["sodium"]

    scores = compute_health_scores(totals)

    session_id = str(uuid.uuid4())
    session = AnalysisSession(
        id=session_id,
        image_url=None,
        detected_foods=[
            {"name": it.food_name, "display_name": it.food_name, "confidence": 1.0}
            for it in req.items
        ],
        status="completed",
    )
    db.add(session)

    meal = Meal(
        session_id=session_id,
        image_url=None,
        detected_foods=display_names,
        total_calories=round(totals["total_calories"], 2),
        protein_g=round(totals["protein_g"], 2),
        carbs_g=round(totals["carbs_g"], 2),
        fat_g=round(totals["fat_g"], 2),
        fiber_g=round(totals["fiber_g"], 2),
        micronutrients={
            "calcium_mg":   round(totals["calcium_mg"], 2),
            "iron_mg":      round(totals["iron_mg"], 2),
            "vitamin_c_mg": round(totals["vitamin_c_mg"], 2),
            "potassium_mg": round(totals["potassium_mg"], 2),
            "sodium_mg":    round(totals["sodium_mg"], 2),
            "vitamin_a_ug": 0.0,
        },
        health_scores=scores,
        question_answers={
            f"{it.food_name}__{k}": v
            for it in req.items
            for k, v in it.answers.items()
        },
    )
    db.add(meal)
    await db.commit()
    await db.refresh(meal)

    return NutritionResult(
        meal_id=meal.id,
        foods=display_names,
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
