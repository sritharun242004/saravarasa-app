from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.client import Client, ClientStatus
from app.models.meal_log import MealLog
from app.models.report import ChallengeReport
from app.models.payment import PaymentTransaction
from app.models.audit import LifestyleAudit
from app.services.compliance_engine import calculate_compliance
from app.services.eligibility_engine import BAND_LABELS

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def admin_dashboard(db: AsyncSession = Depends(get_db)):
    """High-level metrics for the Sarvarasa admin dashboard."""
    clients_r = await db.execute(select(Client))
    clients = clients_r.scalars().all()

    audits_r = await db.execute(
        select(func.count(LifestyleAudit.id)).where(LifestyleAudit.completed == True)
    )
    audit_completed_count = audits_r.scalar() or 0

    payments_r = await db.execute(
        select(func.sum(PaymentTransaction.amount_inr)).where(
            PaymentTransaction.status == "PAID"
        )
    )
    revenue = payments_r.scalar() or 0.0

    status_counts = {
        "total": len(clients),
        "audit_completed": audit_completed_count,
        "active": 0,
        "qualified": 0,
        "second_chance": 0,
        "locked": 0,
        "reactivated": 0,
    }
    for c in clients:
        s = (c.status or "ACTIVE").upper()
        if s == "QUALIFIED":
            status_counts["qualified"] += 1
        elif s == "SECOND_CHANCE":
            status_counts["second_chance"] += 1
        elif s == "LOCKED":
            status_counts["locked"] += 1
        elif s == "ACTIVE":
            status_counts["active"] += 1
        if (c.challenge_cycle or 1) > 2:
            status_counts["reactivated"] += 1

    return {
        **status_counts,
        "revenue_inr": revenue,
    }


@router.get("/clients")
async def list_clients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client))
    clients = result.scalars().all()

    out = []
    for client in clients:
        logs_r = await db.execute(
            select(MealLog).where(
                MealLog.client_id == client.id,
                MealLog.challenge_cycle == (client.challenge_cycle or 1),
            )
        )
        logs = logs_r.scalars().all()
        compliance = calculate_compliance(logs)
        report = await db.get(ChallengeReport, client.id)

        out.append({
            "client_id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "status": client.status,
            "audit_completed": client.audit_completed,
            "challenge_cycle": client.challenge_cycle,
            "compliance_pct": compliance["compliance_pct"],
            "completed_days": compliance["completed_days"],
            "compliance_status": compliance["status"],
            "qualification_status": report.qualification_status if report else None,
            "joined_at": client.joined_at,
        })

    return {"total": len(out), "clients": out}


@router.get("/clients/{client_id}")
async def get_client_detail(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    logs_r = await db.execute(select(MealLog).where(MealLog.client_id == client_id))
    logs = logs_r.scalars().all()

    current_cycle_logs = [l for l in logs if l.challenge_cycle == (client.challenge_cycle or 1)]
    compliance = calculate_compliance(current_cycle_logs)
    report = await db.get(ChallengeReport, client_id)

    audit_r = await db.execute(
        select(LifestyleAudit).where(LifestyleAudit.client_id == client_id)
    )
    audit = audit_r.scalar_one_or_none()

    payments_r = await db.execute(
        select(PaymentTransaction).where(PaymentTransaction.client_id == client_id)
    )
    payments = payments_r.scalars().all()

    return {
        "client": {
            "id": client.id,
            "name": client.name,
            "age": client.age,
            "gender": client.gender,
            "weight_kg": client.weight_kg,
            "goal": client.goal,
            "phone": client.phone,
            "email": client.email,
            "status": client.status,
            "audit_completed": client.audit_completed,
            "challenge_cycle": client.challenge_cycle,
            "joined_at": client.joined_at,
        },
        "audit": {
            "completed": audit.completed if audit else False,
            "sleep_hours": audit.sleep_hours if audit else None,
            "activity_level": audit.activity_level if audit else None,
            "meals_per_day": audit.meals_per_day if audit else None,
            "outside_food_frequency": audit.outside_food_frequency if audit else None,
            "stress_level": audit.stress_level if audit else None,
        } if audit else None,
        "compliance": compliance,
        "meal_timeline": [
            {
                "day": log.day_number,
                "meal_type": log.meal_type,
                "meal_text": log.meal_text,
                "image_url": log.image_url,
                "food_pattern_tags": log.food_pattern_tags or [],
                "challenge_cycle": log.challenge_cycle,
                "submitted_at": log.submitted_at,
            }
            for log in sorted(logs, key=lambda x: (x.challenge_cycle, x.day_number, x.meal_type))
        ],
        "report": {
            "compliance_score": report.compliance_score,
            "completed_days": report.completed_days,
            "qualification_status": report.qualification_status,
            "eligibility_band": report.eligibility_band,
            "band_label": BAND_LABELS.get(report.eligibility_band or "", ""),
            "food_pattern_summary": report.food_pattern_summary or {},
            "food_observations": report.food_observations or [],
            "strengths": report.strengths or [],
            "improvement_areas": report.improvement_areas or [],
            "action_plan": report.action_plan or [],
            "wholesome_plate_tips": report.wholesome_plate_tips or [],
            "generated_at": report.generated_at,
        } if report else None,
        "payment_history": [
            {
                "transaction_id": p.id,
                "amount_inr": p.amount_inr,
                "status": p.status,
                "cycle_unlocked": p.cycle_unlocked,
                "paid_at": p.paid_at,
            }
            for p in payments
        ],
    }


@router.get("/batch/{batch_id}/summary")
async def batch_summary(batch_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.batch_id == batch_id))
    clients = result.scalars().all()

    if not clients:
        raise HTTPException(404, "No clients found for this batch")

    stats = {
        "total": len(clients),
        "audit_completed": 0,
        "qualified": 0,
        "second_chance": 0,
        "locked": 0,
        "active": 0,
    }

    for client in clients:
        if client.audit_completed:
            stats["audit_completed"] += 1
        s = (client.status or "ACTIVE").upper()
        if s in stats:
            stats[s.lower()] = stats.get(s.lower(), 0) + 1

    return {"batch_id": batch_id, **stats}
