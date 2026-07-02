from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, or_

from app.database import get_db
from app.core.security import require_admin
from app.models.client import Client, ClientStatus
from app.models.meal_log import MealLog
from app.models.meal_food import MealFood
from app.models.challenge_attempt import ChallengeAttempt
from app.models.report import ChallengeReport
from app.models.payment import PaymentTransaction
from app.models.audit import LifestyleAudit
from app.models.lifestyle_audit import LifestyleAuditResponse
from app.models.test_attempt import TestAttempt
from app.services.compliance_engine import calculate_compliance
from app.services.challenge_dates import day_dates
from app.services.eligibility_engine import BAND_LABELS

# Every /admin route requires a valid admin token.
router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


@router.get("/dashboard")
async def admin_dashboard(db: AsyncSession = Depends(get_db)):
    """High-level metrics for the Sarvarasa admin dashboard."""
    status_upper = func.upper(Client.status)
    is_active = or_(Client.status.is_(None), status_upper == "ACTIVE")

    counts_r = await db.execute(
        select(
            func.count(Client.id),
            func.count(case((Client.profile_completed == True, 1))),
            func.count(case((status_upper == "QUALIFIED", 1))),
            func.count(case((status_upper == "SECOND_CHANCE", 1))),
            func.count(case((status_upper == "LOCKED", 1))),
            func.count(case((is_active, 1))),
            func.count(case((Client.challenge_cycle > 2, 1))),
        )
    )
    (
        total,
        profile_completed_count,
        qualified_count,
        second_chance_count,
        locked_count,
        active_count,
        reactivated_count,
    ) = counts_r.one()

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

    return {
        "total": total,
        "profile_completed": profile_completed_count,
        "audit_completed": audit_completed_count,
        "active": active_count,
        "qualified": qualified_count,
        "second_chance": second_chance_count,
        "locked": locked_count,
        "reactivated": reactivated_count,
        "revenue_inr": revenue,
    }


@router.get("/clients")
async def list_clients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client))
    clients = result.scalars().all()
    client_ids = [c.id for c in clients]

    # Batch-fetch every client's meal logs and report in two queries instead of
    # issuing two round-trips per client (was 1 + 2N queries for N clients).
    logs_by_client: dict[str, list[MealLog]] = {}
    if client_ids:
        logs_r = await db.execute(select(MealLog).where(MealLog.client_id.in_(client_ids)))
        for log in logs_r.scalars().all():
            logs_by_client.setdefault(log.client_id, []).append(log)

    reports_by_client: dict[str, ChallengeReport] = {}
    if client_ids:
        reports_r = await db.execute(
            select(ChallengeReport).where(ChallengeReport.client_id.in_(client_ids))
        )
        reports_by_client = {r.client_id: r for r in reports_r.scalars().all()}

    out = []
    for client in clients:
        cycle = client.challenge_cycle or 1
        logs = [l for l in logs_by_client.get(client.id, []) if l.challenge_cycle == cycle]
        compliance = calculate_compliance(logs)
        report = reports_by_client.get(client.id)

        out.append({
            "client_id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "sex": client.sex,
            "gender": client.gender,
            "age": client.age,
            "status": client.status,
            "profile_completed": client.profile_completed,
            "audit_completed": client.audit_completed,
            "challenge_cycle": client.challenge_cycle,
            "compliance_pct": compliance["compliance_pct"],
            "completed_days": compliance["completed_days"],
            "compliance_status": compliance["status"],
            "qualification_status": report.qualification_status if report else None,
            "eligibility_band": report.eligibility_band if report else None,
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

    # Filtered in-memory (not a second query) since the full log list is already
    # loaded above for the meal timeline below.
    current_cycle_logs = [l for l in logs if l.challenge_cycle == (client.challenge_cycle or 1)]
    compliance = calculate_compliance(current_cycle_logs)
    report = await db.get(ChallengeReport, client_id)

    # Structured foods per meal log (name, quantity, unit, nutrition).
    foods_by_log_id: dict[str, list] = {}
    if logs:
        foods_r = await db.execute(
            select(MealFood).where(MealFood.meal_log_id.in_([l.id for l in logs]))
        )
        for mf in foods_r.scalars().all():
            foods_by_log_id.setdefault(mf.meal_log_id, []).append(mf)

    # Each challenge cycle's Day 1 date, so every meal log can show its real calendar date.
    attempts_r = await db.execute(
        select(ChallengeAttempt).where(ChallengeAttempt.client_id == client_id)
    )
    day_dates_by_cycle = {a.cycle: day_dates(a.started_at) for a in attempts_r.scalars().all()}

    audit_r = await db.execute(
        select(LifestyleAudit).where(LifestyleAudit.client_id == client_id)
    )
    audit = audit_r.scalar_one_or_none()

    # New scored 35-question lifestyle audit (Phase 2)
    la_r = await db.execute(
        select(LifestyleAuditResponse).where(LifestyleAuditResponse.client_id == client_id)
    )
    lifestyle_audit = la_r.scalar_one_or_none()

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
            "sex": client.sex,
            "height_cm": client.height_cm,
            "weight_kg": client.weight_kg,
            "goal": client.goal,
            "phone": client.phone,
            "email": client.email,
            "status": client.status,
            "profile_completed": client.profile_completed,
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
        "lifestyle_audit": {
            "total_score": lifestyle_audit.total_score,
            "max_score": 65,
            "zone": lifestyle_audit.zone,
            "lowest_domain": lifestyle_audit.lowest_domain,
            "highest_domain": lifestyle_audit.highest_domain,
            "priority_intervention": lifestyle_audit.priority_intervention,
            "bnys_review_required": lifestyle_audit.bnys_review_required,
            "baseline_labs_required": lifestyle_audit.baseline_labs_required,
            "critical_flags": lifestyle_audit.critical_flags or [],
            "domains": {
                "Sleep": (lifestyle_audit.section_b or {}).get("b_weighted"),
                "Food & Eating": (lifestyle_audit.section_c or {}).get("c_weighted"),
                "Movement": (lifestyle_audit.section_d or {}).get("d_weighted"),
                "Stress": (lifestyle_audit.section_e or {}).get("e_weighted"),
                "Digestion": (lifestyle_audit.section_f or {}).get("f_weighted"),
            },
            "completed_at": lifestyle_audit.completed_at,
        } if lifestyle_audit else None,
        "compliance": compliance,
        "meal_timeline": [
            {
                "day": log.day_number,
                "log_date": day_dates_by_cycle.get(log.challenge_cycle, {}).get(log.day_number),
                "meal_type": log.meal_type,
                "meal_text": log.meal_text,
                "logged_time": log.logged_time,
                "image_url": log.image_url,
                "food_pattern_tags": log.food_pattern_tags or [],
                "challenge_cycle": log.challenge_cycle,
                "submitted_at": log.submitted_at,
                "foods": [
                    {
                        "food_id":   mf.food_id,
                        "food_name": mf.food_name or "",
                        "quantity":  mf.quantity,
                        "unit":      mf.unit,
                        "calories":  mf.calories,
                        "protein":   mf.protein,
                        "carbs":     mf.carbs,
                        "fat":       mf.fat,
                    }
                    for mf in foods_by_log_id.get(log.id, [])
                ],
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
        "profile_completed": 0,
        "audit_completed": 0,
        "qualified": 0,
        "second_chance": 0,
        "locked": 0,
        "active": 0,
    }

    for client in clients:
        if client.profile_completed:
            stats["profile_completed"] += 1
        if client.audit_completed:
            stats["audit_completed"] += 1
        s = (client.status or "ACTIVE").upper()
        if s == "QUALIFIED":
            stats["qualified"] += 1
        elif s == "SECOND_CHANCE":
            stats["second_chance"] += 1
        elif s == "LOCKED":
            stats["locked"] += 1
        elif s == "ACTIVE":
            stats["active"] += 1

    return {"batch_id": batch_id, **stats}
