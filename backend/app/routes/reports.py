from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.audit import LifestyleAudit
from app.models.client import Client, ClientStatus
from app.models.meal_log import MealLog
from app.models.meal_food import MealFood
from app.models.report import ChallengeReport
from app.services.compliance_engine import calculate_compliance
from app.services.food_pattern_engine import aggregate_patterns
from app.services.report_engine import build_report
from app.services.eligibility_engine import calculate_eligibility, BAND_LABELS
from app.services.llm_report_engine import generate_llm_report

router = APIRouter(prefix="/reports", tags=["Reports"])

PASS_THRESHOLD = 85.0
REQUIRED_DAYS  = 7


async def _aggregate_nutrition_from_meal_foods(
    db: AsyncSession, log_ids: list[str]
) -> dict:
    if not log_ids:
        return {
            "avg_daily_calories": 0.0,
            "avg_daily_protein":  0.0,
            "avg_daily_fiber":    0.0,
        }

    result = await db.execute(
        select(MealFood).where(MealFood.meal_log_id.in_(log_ids))
    )
    meal_foods = result.scalars().all()

    total_calories = sum(mf.calories or 0 for mf in meal_foods)
    total_protein  = sum(mf.protein  or 0 for mf in meal_foods)
    return {
        "avg_daily_calories": round(total_calories / REQUIRED_DAYS, 1),
        "avg_daily_protein":  round(total_protein  / REQUIRED_DAYS, 1),
        "avg_daily_fiber":    0.0,
    }


@router.post("/generate/{client_id}")
async def generate_report(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")


    # Load meal logs for current cycle
    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.challenge_cycle == client.challenge_cycle,
            )
        )
    )
    logs = result.scalars().all()

    # Load lifestyle audit
    audit_result = await db.execute(
        select(LifestyleAudit).where(LifestyleAudit.client_id == client_id)
    )
    audit = audit_result.scalar_one_or_none()

    compliance     = calculate_compliance(logs)
    compliance_pct = compliance["compliance_pct"]
    completed_days = compliance["completed_days"]

    # Qualification
    if compliance_pct >= PASS_THRESHOLD:
        qualification_status = "QUALIFIED"
    elif client.challenge_cycle == 1:
        qualification_status = "SECOND_CHANCE"
    else:
        qualification_status = "LOCKED"

    pattern_data      = aggregate_patterns(logs)
    food_pattern_pct  = pattern_data.get("percentages", {})

    log_ids    = [log.id for log in logs]
    nutrition  = await _aggregate_nutrition_from_meal_foods(db, log_ids)

    eligibility = calculate_eligibility(
        compliance_pct=compliance_pct,
        protein_pct=food_pattern_pct.get("PROTEIN_PRESENT", 0),
        avg_daily_fiber=nutrition["avg_daily_fiber"],
        avg_daily_calories=nutrition["avg_daily_calories"],
        submitted_days=completed_days,
        submitted_meals=compliance["submitted_meals"],
    )

    # Rule-based report (existing engine)
    report_data = build_report(
        client_name=client.name,
        compliance_pct=compliance_pct,
        completed_days=completed_days,
        food_pattern_pct=food_pattern_pct,
        qualification_status=qualification_status,
        eligibility_score=eligibility["eligibility_score"],
        eligibility_band=eligibility["eligibility_band"],
    )

    # LLM-powered deep report
    llm_data = await generate_llm_report(
        client=client,
        audit=audit,
        meal_logs=logs,
        food_pattern_pct=food_pattern_pct,
        compliance_pct=compliance_pct,
        completed_days=completed_days,
        avg_daily_calories=nutrition["avg_daily_calories"],
        avg_daily_protein=nutrition["avg_daily_protein"],
    )

    # Upsert report
    cr = await db.get(ChallengeReport, client_id)
    if not cr:
        cr = ChallengeReport(client_id=client_id)
        db.add(cr)

    # Rule-based fields
    cr.compliance_score     = compliance_pct
    cr.completed_days       = completed_days
    cr.qualification_status = qualification_status
    cr.eligibility_score    = eligibility["eligibility_score"]
    cr.eligibility_band     = eligibility["eligibility_band"]
    cr.food_observations    = report_data["food_observations"]
    cr.strengths            = report_data["strengths"]
    cr.improvement_areas    = report_data["improvement_areas"]
    cr.action_plan          = report_data["action_plan"]
    cr.wholesome_plate_tips = report_data["wholesome_plate_tips"]
    cr.food_pattern_summary = food_pattern_pct

    # LLM-generated fields
    cr.commitment_level     = llm_data.get("commitment_level")
    cr.commitment_analysis  = llm_data.get("commitment_analysis")
    cr.food_recommendations = llm_data.get("food_recommendations")
    cr.llm_insights         = {
        "personalized_insights":   llm_data.get("personalized_insights", []),
        "seriousness_indicators":  llm_data.get("seriousness_indicators", []),
    }
    cr.llm_summary          = llm_data.get("llm_summary")
    cr.llm_generated_at     = datetime.now(timezone.utc)

    # Update client status
    if qualification_status == "QUALIFIED":
        client.status = ClientStatus.QUALIFIED
    elif qualification_status == "SECOND_CHANCE" and client.challenge_cycle == 1:
        client.status = ClientStatus.SECOND_CHANCE
        client.challenge_cycle = 2
    elif qualification_status == "LOCKED":
        client.status = ClientStatus.LOCKED

    await db.commit()

    return {
        **report_data,
        "band_label":              BAND_LABELS.get(eligibility["eligibility_band"], ""),
        "food_pattern_data":       pattern_data,
        "nutrition_summary": {
            "avg_daily_calories":  nutrition["avg_daily_calories"],
            "avg_daily_protein":   nutrition["avg_daily_protein"],
        },
        # LLM section
        "commitment_level":        llm_data.get("commitment_level"),
        "commitment_analysis":     llm_data.get("commitment_analysis"),
        "seriousness_indicators":  llm_data.get("seriousness_indicators", []),
        "food_recommendations":    llm_data.get("food_recommendations", []),
        "llm_summary":             llm_data.get("llm_summary"),
        "personalized_insights":   llm_data.get("personalized_insights", []),
        "llm_generated_at":        cr.llm_generated_at.isoformat() if cr.llm_generated_at else None,
    }


@router.get("/{client_id}")
async def get_report(client_id: str, db: AsyncSession = Depends(get_db)):
    cr = await db.get(ChallengeReport, client_id)
    if not cr:
        raise HTTPException(
            404,
            "No report found. Complete 6+ days with all 3 meals, then generate your report.",
        )

    client = await db.get(Client, client_id)
    llm_insights = cr.llm_insights or {}

    return {
        # Rule-based fields
        "client_name":             client.name if client else "Unknown",
        "compliance_score":        cr.compliance_score,
        "completed_days":          cr.completed_days,
        "qualification_status":    cr.qualification_status,
        "eligibility_band":        cr.eligibility_band,
        "band_label":              BAND_LABELS.get(cr.eligibility_band or "", ""),
        "food_observations":       cr.food_observations or [],
        "strengths":               cr.strengths or [],
        "improvement_areas":       cr.improvement_areas or [],
        "action_plan":             cr.action_plan or [],
        "wholesome_plate_tips":    cr.wholesome_plate_tips or [],
        "food_pattern_summary":    cr.food_pattern_summary or {},
        "generated_at":            cr.generated_at,
        # LLM fields
        "commitment_level":        cr.commitment_level,
        "commitment_analysis":     cr.commitment_analysis,
        "seriousness_indicators":  llm_insights.get("seriousness_indicators", []),
        "food_recommendations":    cr.food_recommendations or [],
        "llm_summary":             cr.llm_summary,
        "personalized_insights":   llm_insights.get("personalized_insights", []),
        "llm_generated_at":        cr.llm_generated_at,
    }
