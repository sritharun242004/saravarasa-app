from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.client import Client
from app.core.security import hash_password, verify_password, create_token, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    goal: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Client).where(Client.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "An account with this email already exists")

    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    client = Client(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        phone=req.phone,
        age=req.age,
        gender=req.gender,
        goal=req.goal,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)

    token = create_token(client.id)
    return {
        "client_id": client.id,
        "name": client.name,
        "email": client.email,
        "status": client.status,
        "token": token,
    }


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.email == req.email))
    client = result.scalar_one_or_none()

    if not client or not client.password_hash:
        raise HTTPException(401, "Invalid email or password")
    if not verify_password(req.password, client.password_hash):
        raise HTTPException(401, "Invalid email or password")

    token = create_token(client.id)
    return {
        "client_id": client.id,
        "name": client.name,
        "email": client.email,
        "status": client.status,
        "audit_completed": client.audit_completed,
        "token": token,
    }


@router.get("/me")
async def me(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    token = authorization.removeprefix("Bearer ")
    client_id = decode_token(token)
    if not client_id:
        raise HTTPException(401, "Invalid or expired token")

    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Account not found")

    return {
        "client_id": client.id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "age": client.age,
        "gender": client.gender,
        "status": client.status,
        "audit_completed": client.audit_completed,
        "challenge_cycle": client.challenge_cycle,
    }
