import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text

from app.database import get_db
from app.config import settings
from app.models.client import Client
from app.models.meal_log import MealLog, MealType
from app.models.meal_food import MealFood
from app.models.challenge_attempt import ChallengeAttempt
from app.services.compliance_engine import calculate_compliance
from app.services.food_pattern_engine import classify_meal
from app.services.food_search_service import (
    _food_search_service,
    calc_nutrition,
    grams_for,
)
from app.services.food_llm_fallback import fallback_food_recognition_sync

router = APIRouter(prefix="/challenge", tags=["Challenge"])

VALID_MEAL_TYPES = {m.value for m in MealType}
REQUIRED_TYPES = {"BREAKFAST", "LUNCH", "DINNER"}


async def _save_image(file: UploadFile) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "meal.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.upload_dir, filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


def _auto_meal_text(foods: list[dict], quick_add_text: str = "") -> str:
    """Build a readable meal_text string from structured foods + optional free text."""
    parts = [f"{f['quantity']} {f['unit']} {f['food_name']}" for f in foods]
    base = ", ".join(parts)
    if quick_add_text:
        return f"{base} | {quick_add_text}".strip(" |") if base else quick_add_text
    return base or "Meal submitted"


async def _create_meal_foods(
    db: AsyncSession,
    meal_log_id: str,
    foods_raw: list[dict],
) -> list[dict]:
    """
    Create MealFood records for each structured food item.
    Returns a list of nutrition summaries for client feedback.
    """
    results = []
    for item in foods_raw:
        food_id   = item.get("food_id", "")
        food_name = item.get("food_name", "")
        quantity  = float(item.get("quantity", 1))
        unit      = item.get("unit", "g")

        # Look up food from DB to get accurate per-100g nutrients
        food_detail = await _food_search_service.get_food(food_id, db)

        if food_detail:
            nutrition = calc_nutrition(food_detail, quantity, unit)
        else:
            # Food not found in DB — try LLM fallback for recognition & nutrition estimation
            print(f"[Food LLM Fallback] Food ID '{food_id}' / '{food_name}' not found, using LLM...")
            llm_result = fallback_food_recognition_sync(food_name or food_id)

            if llm_result and llm_result.get("recognized"):
                # LLM recognized the food, use estimated nutrition
                food_detail = {
                    "food_name": llm_result.get("canonical_name", food_name or food_id),
                    "energy_kcal": llm_result.get("energy_kcal", 0),
                    "protein_g": llm_result.get("protein_g", 0),
                    "carb_g": llm_result.get("carb_g", 0),
                    "fat_g": llm_result.get("fat_g", 0),
                }
                nutrition = calc_nutrition(food_detail, quantity, unit)
                food_name = llm_result.get("canonical_name", food_name or food_id)
                print(f"[Food LLM Fallback] Recognized as: {food_name} (confidence: {llm_result.get('confidence', 0)})")
            else:
                # LLM couldn't recognize — store zeros
                print(f"[Food LLM Fallback] Could not recognize '{food_name or food_id}', storing zeros")
                nutrition = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
                food_name = food_name or food_id

        display_name = food_detail["food_name"] if food_detail else food_name
        mf = MealFood(
            meal_log_id=meal_log_id,
            food_id=food_id if food_detail else None,
            food_name=display_name,
            quantity=grams_for(quantity, unit, display_name),
            unit=unit,
            calories=nutrition["calories"],
            protein=nutrition["protein"],
            carbs=nutrition["carbs"],
            fat=nutrition["fat"],
        )
        db.add(mf)
        results.append({
            "food_name": display_name,
            **nutrition,
        })

    await db.flush()   # write meal_foods before commit
    return results


async def _delete_meal_foods(db: AsyncSession, meal_log_id: str) -> None:
    """Remove all meal_foods for a given meal log (used on upsert)."""
    await db.execute(
        text("DELETE FROM meal_foods WHERE meal_log_id = :id"),
        {"id": meal_log_id},
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/submit-meal")
async def submit_meal(
    client_id:       str              = Form(...),
    day_number:      int              = Form(...),
    meal_type:       str              = Form(...),
    meal_text:       str              = Form(""),        # optional — auto-generated from foods
    foods_json:      Optional[str]    = Form(None),      # JSON list of StructuredFood
    quick_add_text:  Optional[str]    = Form(None),      # free-text fallback
    image:           Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a meal for the 7-day challenge.

    Accepts either:
    - Structured foods (foods_json) — preferred; creates meal_foods records
    - Free text (meal_text) — legacy / quick-add fallback
    - Both at once (foods_json + quick_add_text)

    Image is required for compliance photo evidence.
    """
    meal_type_upper = meal_type.upper()
    if meal_type_upper not in VALID_MEAL_TYPES:
        raise HTTPException(400, f"meal_type must be one of {sorted(VALID_MEAL_TYPES)}")
    if not 1 <= day_number <= 7:
        raise HTTPException(400, "day_number must be between 1 and 7")
    has_image = image and image.filename

    # Parse structured foods
    foods_raw: list[dict] = []
    if foods_json:
        try:
            foods_raw = json.loads(foods_json)
            if not isinstance(foods_raw, list):
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            raise HTTPException(400, "foods_json must be a valid JSON array")

    # Derive meal_text
    effective_text = meal_text.strip() or ""
    if not effective_text:
        effective_text = _auto_meal_text(foods_raw, quick_add_text or "")
    if not effective_text:
        raise HTTPException(400, "Provide at least one food item or a meal description")

    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    # Check day-by-day restriction: user can only submit for current day or earlier (if updating)
    attempt_result = await db.execute(
        select(ChallengeAttempt).where(
            and_(
                ChallengeAttempt.client_id == client_id,
                ChallengeAttempt.cycle == client.challenge_cycle,
            )
        )
    )
    attempt = attempt_result.scalar_one_or_none()

    if attempt and attempt.started_at:
        now = datetime.now(timezone.utc)
        days_elapsed = (now - attempt.started_at).days
        current_day = min(days_elapsed + 1, 7)  # Current day in challenge (1-7)

        # Check if trying to submit for a future day
        if day_number > current_day:
            raise HTTPException(
                403,
                f"You can only submit meals for Day {current_day} or earlier. Day {day_number} is not yet available."
            )

    # Classify meal pattern from the effective text
    pattern_tags = [k for k, v in classify_meal(effective_text).items() if v]

    # Upsert meal log
    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.day_number == day_number,
                MealLog.meal_type == meal_type_upper,
                MealLog.challenge_cycle == client.challenge_cycle,
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Keep old image if no new one supplied
        if has_image:
            existing.image_url = await _save_image(image)
        image_url = existing.image_url or ""
        existing.meal_text         = effective_text
        existing.food_pattern_tags = pattern_tags
        await db.flush()
        await _delete_meal_foods(db, existing.id)
        food_summaries = await _create_meal_foods(db, existing.id, foods_raw)
        await db.commit()
        return {
            "log_id":            existing.id,
            "updated":           True,
            "day":               day_number,
            "meal_type":         meal_type_upper,
            "image_url":         image_url,
            "food_pattern_tags": pattern_tags,
            "foods":             food_summaries,
        }

    # New submission — image is required for first submission
    if not has_image:
        raise HTTPException(400, "A meal photo is required for the first submission")
    image_url = await _save_image(image)

    log = MealLog(
        client_id=client_id,
        day_number=day_number,
        meal_type=meal_type_upper,
        meal_text=effective_text,
        image_url=image_url,
        food_pattern_tags=pattern_tags,
        challenge_cycle=client.challenge_cycle,
    )
    db.add(log)
    await db.flush()  # assigns log.id

    food_summaries = await _create_meal_foods(db, log.id, foods_raw)
    await db.commit()
    await db.refresh(log)

    return {
        "log_id":            log.id,
        "updated":           False,
        "day":               day_number,
        "meal_type":         meal_type_upper,
        "image_url":         image_url,
        "food_pattern_tags": pattern_tags,
        "foods":             food_summaries,
    }


@router.get("/meal-foods/{meal_log_id}")
async def get_meal_foods(meal_log_id: str, db: AsyncSession = Depends(get_db)):
    """Return all structured food entries for a given meal log."""
    result = await db.execute(
        select(MealFood).where(MealFood.meal_log_id == meal_log_id)
    )
    meal_foods = result.scalars().all()
    return [
        {
            "id":        mf.id,
            "food_id":   mf.food_id,
            "food_name": mf.food_name or "",
            "quantity":  mf.quantity,
            "unit":      mf.unit,
            "calories":  mf.calories,
            "protein":   mf.protein,
            "carbs":     mf.carbs,
            "fat":       mf.fat,
        }
        for mf in meal_foods
    ]


@router.get("/progress/{client_id}")
async def get_progress(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.challenge_cycle == client.challenge_cycle,
            )
        )
    )
    logs = result.scalars().all()
    compliance = calculate_compliance(logs)

    # Calculate current day based on challenge start
    attempt_result = await db.execute(
        select(ChallengeAttempt).where(
            and_(
                ChallengeAttempt.client_id == client_id,
                ChallengeAttempt.cycle == client.challenge_cycle,
            )
        )
    )
    attempt = attempt_result.scalar_one_or_none()

    current_day = 1
    if attempt and attempt.started_at:
        now = datetime.now(timezone.utc)
        days_elapsed = (now - attempt.started_at).days
        current_day = min(days_elapsed + 1, 7)

    # Calculate consistency: measure if user submitted meals consistently each day
    # Track which days have all 3 meals submitted
    completed_days = compliance.get("completed_days", 0)
    consistency_pct = (completed_days / 7) * 100 if completed_days > 0 else 0.0

    return {
        "client_id":      client_id,
        "client_name":    client.name,
        "client_status":  client.status,
        "challenge_cycle": client.challenge_cycle,
        "audit_completed": client.audit_completed,
        "current_day":    current_day,
        "consistency_pct": round(consistency_pct, 1),
        **compliance,
    }


@router.get("/day/{client_id}/{day}")
async def get_day_meals(client_id: str, day: int, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.day_number == day,
                MealLog.challenge_cycle == client.challenge_cycle,
            )
        )
    )
    logs = result.scalars().all()

    # Attach meal_foods for each log
    meals_with_foods = []
    for log in sorted(logs, key=lambda x: x.meal_type):
        mf_result = await db.execute(
            select(MealFood).where(MealFood.meal_log_id == log.id)
        )
        meal_foods = mf_result.scalars().all()
        meals_with_foods.append({
            "meal_type":        log.meal_type,
            "meal_text":        log.meal_text,
            "image_url":        log.image_url,
            "food_pattern_tags": log.food_pattern_tags or [],
            "submitted_at":     log.submitted_at,
            "foods": [
                {
                    "id":        mf.id,
                    "food_id":   mf.food_id,
                    "food_name": mf.food_name or "",
                    "quantity":  mf.quantity,
                    "unit":      mf.unit,
                    "calories":  mf.calories,
                    "protein":   mf.protein,
                    "carbs":     mf.carbs,
                    "fat":       mf.fat,
                }
                for mf in meal_foods
            ],
            "nutrition_total": {
                "calories": round(sum(mf.calories for mf in meal_foods), 1),
                "protein":  round(sum(mf.protein  for mf in meal_foods), 1),
                "carbs":    round(sum(mf.carbs    for mf in meal_foods), 1),
                "fat":      round(sum(mf.fat      for mf in meal_foods), 1),
            },
        })

    submitted_types = {log.meal_type for log in logs}
    required_types  = {"BREAKFAST", "LUNCH", "DINNER"}

    return {
        "day":            day,
        "challenge_cycle": client.challenge_cycle,
        "is_complete":    required_types.issubset(submitted_types),
        "meals":          meals_with_foods,
    }
