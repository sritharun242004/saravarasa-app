from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.core.security import get_current_client, require_owner
from app.models.client import Client
from app.models.lifestyle_audit import LifestyleAuditQuestion, LifestyleAuditResponse
from app.services.audit_evaluation_engine import evaluate_audit

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/questions")
async def get_audit_questions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LifestyleAuditQuestion).order_by(LifestyleAuditQuestion.question_number))
    questions = result.scalars().all()
    return {
        "total": len(questions),
        "questions": [
            {
                "id": q.id,
                "section": q.section,
                "number": q.question_number,
                "text": q.question_text,
                "type": q.input_type,
                "options": q.options or []
            }
            for q in questions
        ]
    }


@router.post("/submit/{client_id}")
async def submit_audit(
    client_id: str,
    responses: dict,
    db: AsyncSession = Depends(get_db),
    current_client: str = Depends(get_current_client),
):
    require_owner(client_id, current_client)
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    try:
        evaluation = evaluate_audit(responses)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Failed to evaluate audit: {str(e)}")

    # Upsert one audit response per client (re-takes overwrite the previous result).
    existing = await db.execute(
        select(LifestyleAuditResponse).where(LifestyleAuditResponse.client_id == client_id)
    )
    record = existing.scalar_one_or_none()
    if record is None:
        record = LifestyleAuditResponse(id=str(uuid.uuid4()), client_id=client_id)
        db.add(record)

    record.section_a = responses.get("section_a", {})
    record.section_b = evaluation.get("section_b", {})
    record.section_c = evaluation.get("section_c", {})
    record.section_d = evaluation.get("section_d", {})
    record.section_e = evaluation.get("section_e", {})
    record.section_f = evaluation.get("section_f", {})
    record.total_score = evaluation.get("total_score")
    record.zone = evaluation.get("zone")
    record.lowest_domain = evaluation.get("lowest_domain")
    record.highest_domain = evaluation.get("highest_domain")
    record.critical_flags = evaluation.get("critical_flags", [])
    record.bnys_review_required = evaluation.get("bnys_review_required", False)
    record.baseline_labs_required = evaluation.get("baseline_labs_required", False)
    record.priority_intervention = evaluation.get("priority_intervention", "")
    record.completed_at = datetime.utcnow()

    # Reflect completion on the client so it surfaces in profile + admin.
    client.audit_completed = True

    await db.commit()

    return {
        "success": True,
        "score": evaluation.get("total_score"),
        "max_score": 65,
        "zone": evaluation.get("zone"),
        "message": evaluation.get("zone_message"),
        "lowest_domain": evaluation.get("lowest_domain"),
        "highest_domain": evaluation.get("highest_domain"),
        "priority_intervention": evaluation.get("priority_intervention"),
        "critical_flags": evaluation.get("critical_flags"),
        "bnys_review_required": evaluation.get("bnys_review_required"),
    }


@router.get("/result/{client_id}")
async def get_audit_result(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_client: str = Depends(get_current_client),
):
    require_owner(client_id, current_client)
    result = await db.execute(
        select(LifestyleAuditResponse).where(LifestyleAuditResponse.client_id == client_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(404, "No audit result found")

    # Per-domain weighted contributions for the profile breakdown.
    domains = {
        "Sleep": (record.section_b or {}).get("b_weighted"),
        "Food & Eating": (record.section_c or {}).get("c_weighted"),
        "Movement": (record.section_d or {}).get("d_weighted"),
        "Stress": (record.section_e or {}).get("e_weighted"),
        "Digestion": (record.section_f or {}).get("f_weighted"),
    }

    return {
        "client_id": record.client_id,
        "total_score": record.total_score,
        "max_score": 65,
        "zone": record.zone,
        "lowest_domain": record.lowest_domain,
        "highest_domain": record.highest_domain,
        "priority_intervention": record.priority_intervention,
        "bnys_review_required": record.bnys_review_required,
        "domains": domains,
        "completed_at": record.completed_at,
    }
