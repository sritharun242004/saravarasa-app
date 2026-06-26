from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from pydantic import BaseModel
from app.database import AsyncSessionLocal
from app.models.client import Client
from app.core.validation import validate_email_deliverable, normalize_phone, validate_name

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    sex: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None


class ProfileResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    sex: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    profile_completed: bool

    class Config:
        from_attributes = True


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/{client_id}", response_model=ProfileResponse)
async def get_profile(client_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ProfileResponse)
async def update_profile(client_id: str, profile_update: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = profile_update.dict(exclude_unset=True)

    # Normalize + validate the same way signup does.
    if update_data.get("name") is not None:
        update_data["name"] = validate_name(update_data["name"])
    if update_data.get("phone") is not None:
        update_data["phone"] = normalize_phone(update_data["phone"], required=True)
    if update_data.get("email") is not None:
        new_email = validate_email_deliverable(update_data["email"])
        dupe = await db.execute(
            select(Client.id)
            .where(func.lower(Client.email) == new_email, Client.id != client_id)
            .limit(1)
        )
        if dupe.first() is not None:
            raise HTTPException(409, "That email is already in use by another account")
        update_data["email"] = new_email

    for field, value in update_data.items():
        if value is not None:
            setattr(client, field, value)

    if client.name and client.email and client.phone and client.sex and client.gender:
        client.profile_completed = True

    client.profile_updated_at = datetime.utcnow()
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client
