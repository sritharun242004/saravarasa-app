from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.client import Client, ChallengeBatch

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


class RegisterRequest(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    batch_id: Optional[str] = None


class CreateBatchRequest(BaseModel):
    name: str
    capacity: Optional[int] = 100


@router.post("/register")
async def register_client(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if req.batch_id:
        batch = await db.get(ChallengeBatch, req.batch_id)
        if not batch:
            raise HTTPException(404, "Batch not found")

    client = Client(**req.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return {
        "client_id": client.id,
        "name": client.name,
        "status": client.status,
        "batch_id": client.batch_id,
    }


@router.get("/batches")
async def list_batches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChallengeBatch))
    batches = result.scalars().all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "start_date": b.start_date,
            "end_date": b.end_date,
            "capacity": b.capacity,
        }
        for b in batches
    ]


@router.post("/batches")
async def create_batch(req: CreateBatchRequest, db: AsyncSession = Depends(get_db)):
    batch = ChallengeBatch(name=req.name, capacity=req.capacity)
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    return {"batch_id": batch.id, "name": batch.name, "capacity": batch.capacity}
