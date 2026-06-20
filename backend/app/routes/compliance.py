from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.client import Client
from app.models.meal_log import MealLog
from app.services.compliance_engine import calculate_compliance

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.get("/{client_id}")
async def get_client_compliance(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(select(MealLog).where(MealLog.client_id == client_id))
    logs = result.scalars().all()
    return {"client_id": client_id, "client_name": client.name, **calculate_compliance(logs)}


@router.get("/batch/{batch_id}")
async def get_batch_compliance(batch_id: str, db: AsyncSession = Depends(get_db)):
    clients_result = await db.execute(select(Client).where(Client.batch_id == batch_id))
    clients = clients_result.scalars().all()

    if not clients:
        raise HTTPException(404, "No clients found for this batch")

    summary = []
    for client in clients:
        logs_result = await db.execute(select(MealLog).where(MealLog.client_id == client.id))
        logs = logs_result.scalars().all()
        c = calculate_compliance(logs)
        summary.append({"client_id": client.id, "client_name": client.name, **c})

    passing = sum(1 for s in summary if s["status"] in ("QUALIFIED", "COMPLETE", "PASSING"))
    avg_pct = round(sum(s["compliance_pct"] for s in summary) / len(summary), 1) if summary else 0

    return {
        "batch_id": batch_id,
        "total_clients": len(clients),
        "passing": passing,
        "failed": len(clients) - passing,
        "average_compliance_pct": avg_pct,
        "clients": summary,
    }
