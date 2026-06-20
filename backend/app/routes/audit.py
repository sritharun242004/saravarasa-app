from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.client import Client
from app.models.audit import LifestyleAudit

router = APIRouter(prefix="/audit", tags=["Audit"])


class AuditPayload(BaseModel):
    client_id: str
    # Basic Profile
    city: Optional[str] = None
    occupation: Optional[str] = None
    cooking_at_home: Optional[bool] = None
    # Sleep
    sleep_hours: Optional[str] = None
    sleep_quality: Optional[str] = None
    wake_time: Optional[str] = None
    # Food Habits
    meals_per_day: Optional[str] = None
    breakfast_habit: Optional[str] = None
    water_intake: Optional[str] = None
    outside_food_frequency: Optional[str] = None
    sugary_beverage_frequency: Optional[str] = None
    processed_food_frequency: Optional[str] = None
    # Movement
    activity_level: Optional[str] = None
    exercise_frequency: Optional[str] = None
    # Stress
    stress_level: Optional[str] = None
    stress_eating: Optional[str] = None
    # Digestive Health
    digestion_issues: Optional[bool] = None
    digestion_notes: Optional[str] = None
    bowel_regularity: Optional[str] = None
    # Goals
    health_goals: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    # Completion flag
    completed: Optional[bool] = False


@router.post("/save")
async def save_audit(payload: AuditPayload, db: AsyncSession = Depends(get_db)):
    """Auto-save audit (partial or complete). Creates or updates the audit record."""
    client = await db.get(Client, payload.client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    audit = await db.get(LifestyleAudit, payload.client_id)
    if not audit:
        audit = LifestyleAudit(id=payload.client_id, client_id=payload.client_id)
        db.add(audit)

    fields = payload.model_dump(exclude={"client_id"}, exclude_none=True)
    for field, value in fields.items():
        setattr(audit, field, value)

    if payload.completed:
        audit.completed = True
        audit.completed_at = datetime.now(timezone.utc)
        client.audit_completed = True

    await db.commit()
    await db.refresh(audit)
    return {
        "audit_id": audit.id,
        "client_id": audit.client_id,
        "completed": audit.completed,
        "message": "Audit completed — challenge unlocked!" if audit.completed else "Progress saved.",
    }


@router.get("/{client_id}")
async def get_audit(client_id: str, db: AsyncSession = Depends(get_db)):
    audit = await db.get(LifestyleAudit, client_id)
    if not audit:
        raise HTTPException(404, "No audit found for this client")
    return {
        "audit_id": audit.id,
        "client_id": audit.client_id,
        "city": audit.city,
        "occupation": audit.occupation,
        "cooking_at_home": audit.cooking_at_home,
        "sleep_hours": audit.sleep_hours,
        "sleep_quality": audit.sleep_quality,
        "wake_time": audit.wake_time,
        "meals_per_day": audit.meals_per_day,
        "breakfast_habit": audit.breakfast_habit,
        "water_intake": audit.water_intake,
        "outside_food_frequency": audit.outside_food_frequency,
        "sugary_beverage_frequency": audit.sugary_beverage_frequency,
        "processed_food_frequency": audit.processed_food_frequency,
        "activity_level": audit.activity_level,
        "exercise_frequency": audit.exercise_frequency,
        "stress_level": audit.stress_level,
        "stress_eating": audit.stress_eating,
        "digestion_issues": audit.digestion_issues,
        "digestion_notes": audit.digestion_notes,
        "bowel_regularity": audit.bowel_regularity,
        "health_goals": audit.health_goals,
        "dietary_restrictions": audit.dietary_restrictions,
        "completed": audit.completed,
        "completed_at": audit.completed_at,
    }
