import json
import os
import re
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text

from app.database import get_db
from app.config import settings
from app.core.security import get_current_client, require_owner
from app.models.client import Client
from app.models.meal_log import MealLog, MealType
from app.models.meal_food import MealFood
from app.models.challenge_attempt import ChallengeAttempt
from app.services.challenge_dates import day_dates
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
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


async def _current_day(db: AsyncSession, client_id: str, challenge_cycle: int) -> int:
    """The next day still needing all 3 meals — days must be logged 1 through 7 in order."""
    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.challenge_cycle == challenge_cycle,
            )
        )
    )
    compliance = calculate_compliance(result.scalars().all())
    return min(compliance.get("completed_days", 0) + 1, 7)


async def _get_or_create_attempt(db: AsyncSession, client_id: str, cycle: int) -> ChallengeAttempt:
    """The anchor for this cycle's Day 1 date — created on the first meal ever logged."""
    result = await db.execute(
        select(ChallengeAttempt).where(
            and_(ChallengeAttempt.client_id == client_id, ChallengeAttempt.cycle == cycle)
        )
    )
    attempt = result.scalar_one_or_none()
    if attempt is not None:
        return attempt

    # Backfill for clients who logged meals before this feature existed — anchor
    # Day 1 to their actual first submission instead of "today".
    earliest_result = await db.execute(
        select(func.min(MealLog.submitted_at)).where(
            and_(MealLog.client_id == client_id, MealLog.challenge_cycle == cycle)
        )
    )
    earliest = earliest_result.scalar()

    attempt = ChallengeAttempt(client_id=client_id, cycle=cycle)
    if earliest is not None:
        attempt.started_at = earliest
    db.add(attempt)
    await db.flush()
    return attempt


# Content-Type -> (extension, magic-byte signatures to verify against). The
# extension written to disk is always derived from this whitelist, never from
# the caller-supplied filename — an attacker-chosen filename must never decide
# what gets written into the publicly served uploads directory.
_ALLOWED_IMAGE_TYPES: dict[str, tuple[str, tuple[bytes, ...]]] = {
    "image/jpeg": (".jpg", (b"\xff\xd8\xff",)),
    "image/png":  (".png", (b"\x89PNG\r\n\x1a\n",)),
    "image/webp": (".webp", (b"RIFF",)),
    "image/heic": (".heic", (b"ftyp",)),
    "image/heif": (".heif", (b"ftyp",)),
}


async def _save_image(file: UploadFile) -> str:
    content_type = (file.content_type or "").lower().split(";")[0].strip()
    match = _ALLOWED_IMAGE_TYPES.get(content_type)
    if not match:
        raise HTTPException(400, "Only JPEG, PNG, WEBP, or HEIC/HEIF images are allowed")
    ext, signatures = match

    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty image upload")
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(400, f"Image exceeds the {settings.max_upload_size_mb}MB limit")
    # HEIC/HEIF's "ftyp" box signature starts at byte offset 4, not 0.
    header = content[:16]
    if not any(sig in header[:12] for sig in signatures):
        raise HTTPException(400, "Uploaded file does not match its declared image type")

    os.makedirs(settings.upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.upload_dir, filename)
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


def _auto_meal_text(foods: list[dict]) -> str:
    """Build a readable meal_text string from structured foods."""
    parts = [f"{f['quantity']} {f['unit']} {f['food_name']}" for f in foods]
    return ", ".join(parts) or "Meal submitted"


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
        db_matched = food_detail is not None  # only true for a real `foods` table row

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
            food_id=food_id if db_matched else None,
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
    logged_time:     Optional[str]    = Form(None),      # user-entered time, "HH:MM"
    image:           Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_client:  str              = Depends(get_current_client),
):
    """
    Submit a meal for the 7-day challenge.

    Foods are always structured (foods_json) — including foods typed in freely
    that don't match the food database, which are still saved with the name
    the user entered. Image and a manually-entered time are required.
    """
    require_owner(client_id, current_client)
    meal_type_upper = meal_type.upper()
    if meal_type_upper not in VALID_MEAL_TYPES:
        raise HTTPException(400, f"meal_type must be one of {sorted(VALID_MEAL_TYPES)}")
    if not 1 <= day_number <= 7:
        raise HTTPException(400, "day_number must be between 1 and 7")
    has_image = image and image.filename

    if logged_time and not _TIME_RE.match(logged_time):
        raise HTTPException(400, "logged_time must be in HH:MM 24-hour format")

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
    effective_text = meal_text.strip() or _auto_meal_text(foods_raw)
    if not effective_text:
        raise HTTPException(400, "Provide at least one food item or a meal description")

    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    # Days must be logged in order — day N opens only once day N-1 has all 3 meals.
    current_day = await _current_day(db, client_id, client.challenge_cycle)
    if day_number > current_day:
        raise HTTPException(
            403,
            f"Complete Day {current_day} before logging Day {day_number}."
        )

    # Anchor Day 1's date to the first meal ever logged this cycle — every other
    # day's date follows automatically, one calendar day after another.
    attempt = await _get_or_create_attempt(db, client_id, client.challenge_cycle)
    log_date = day_dates(attempt.started_at)[day_number]

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
        # Keep old image/time if no new one supplied
        if has_image:
            existing.image_url = await _save_image(image)
        if logged_time:
            existing.logged_time = logged_time
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
            "log_date":          log_date,
            "meal_type":         meal_type_upper,
            "image_url":         image_url,
            "logged_time":       existing.logged_time,
            "food_pattern_tags": pattern_tags,
            "foods":             food_summaries,
        }

    # New submission — image and the time eaten are required for the first submission
    if not has_image:
        raise HTTPException(400, "A meal photo is required for the first submission")
    if not logged_time:
        raise HTTPException(400, "The time you ate this meal is required")
    image_url = await _save_image(image)

    log = MealLog(
        client_id=client_id,
        day_number=day_number,
        meal_type=meal_type_upper,
        meal_text=effective_text,
        image_url=image_url,
        food_pattern_tags=pattern_tags,
        challenge_cycle=client.challenge_cycle,
        logged_time=logged_time,
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
        "log_date":          log_date,
        "meal_type":         meal_type_upper,
        "image_url":         image_url,
        "logged_time":       log.logged_time,
        "food_pattern_tags": pattern_tags,
        "foods":             food_summaries,
    }


@router.get("/meal-foods/{meal_log_id}")
async def get_meal_foods(
    meal_log_id: str,
    db: AsyncSession = Depends(get_db),
    current_client: str = Depends(get_current_client),
):
    """Return all structured food entries for a given meal log."""
    log = await db.get(MealLog, meal_log_id)
    if not log or log.client_id != current_client:
        raise HTTPException(404, "Meal log not found")

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
async def get_progress(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_client: str = Depends(get_current_client),
):
    require_owner(client_id, current_client)
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

    # Days are logged in order — current day is the next one still needing all 3 meals.
    completed_days = compliance.get("completed_days", 0)
    current_day = min(completed_days + 1, 7)

    # Calculate consistency: measure if user submitted meals consistently each day
    consistency_pct = (completed_days / 7) * 100 if completed_days > 0 else 0.0

    # Day 1's date through Day 7's date, back to back — only known once the first
    # meal has been logged (read-only here; submit-meal is what creates the anchor).
    attempt_result = await db.execute(
        select(ChallengeAttempt).where(
            and_(ChallengeAttempt.client_id == client_id, ChallengeAttempt.cycle == client.challenge_cycle)
        )
    )
    attempt = attempt_result.scalar_one_or_none()
    days_map = day_dates(attempt.started_at) if attempt else {}

    return {
        "client_id":      client_id,
        "client_name":    client.name,
        "client_status":  client.status,
        "challenge_cycle": client.challenge_cycle,
        "audit_completed": client.audit_completed,
        "current_day":    current_day,
        "consistency_pct": round(consistency_pct, 1),
        "challenge_start_date": days_map.get(1),
        "day_dates":      days_map,
        **compliance,
    }


@router.get("/day/{client_id}/{day}")
async def get_day_meals(
    client_id: str,
    day: int,
    db: AsyncSession = Depends(get_db),
    current_client: str = Depends(get_current_client),
):
    require_owner(client_id, current_client)
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

    # Attach meal_foods for each log — one batched query instead of one per log.
    foods_by_log_id: dict[str, list] = {}
    if logs:
        foods_r = await db.execute(
            select(MealFood).where(MealFood.meal_log_id.in_([l.id for l in logs]))
        )
        for mf in foods_r.scalars().all():
            foods_by_log_id.setdefault(mf.meal_log_id, []).append(mf)

    meals_with_foods = []
    for log in sorted(logs, key=lambda x: x.meal_type):
        meal_foods = foods_by_log_id.get(log.id, [])
        meals_with_foods.append({
            "meal_type":        log.meal_type,
            "meal_text":        log.meal_text,
            "image_url":        log.image_url,
            "logged_time":      log.logged_time,
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

    attempt_result = await db.execute(
        select(ChallengeAttempt).where(
            and_(ChallengeAttempt.client_id == client_id, ChallengeAttempt.cycle == client.challenge_cycle)
        )
    )
    attempt = attempt_result.scalar_one_or_none()
    log_date = day_dates(attempt.started_at)[day] if attempt else None

    return {
        "day":            day,
        "log_date":       log_date,
        "challenge_cycle": client.challenge_cycle,
        "is_complete":    required_types.issubset(submitted_types),
        "meals":          meals_with_foods,
    }
