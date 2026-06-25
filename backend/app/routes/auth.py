from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.config import settings
from app.models.client import Client
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.core.cognito import (
    cognito_configured,
    exchange_code_for_tokens,
    verify_id_token,
)

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


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/admin/login")
async def admin_login(req: AdminLoginRequest):
    """Authenticate the single configured admin and return an admin token."""
    if not settings.admin_email or not settings.admin_password:
        raise HTTPException(503, "Admin login is not configured")
    if (
        req.email.strip().lower() != settings.admin_email.strip().lower()
        or req.password != settings.admin_password
    ):
        raise HTTPException(401, "Invalid admin credentials")
    return {
        "token": create_token(settings.admin_email),
        "email": settings.admin_email,
        "is_admin": True,
    }


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


class CognitoExchangeRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None


async def _upsert_oauth_client(db: AsyncSession, claims: dict) -> Client:
    """Find-or-create a Client from verified Cognito ID-token claims.

    Every federated (Google) sign-in lands a row in the `clients` table, so the
    user shows up in the admin database alongside email/password sign-ups.
    """
    email = (claims.get("email") or "").lower().strip()
    if not email:
        raise HTTPException(400, "Cognito token did not include an email claim")

    name = (
        claims.get("name")
        or claims.get("given_name")
        or email.split("@")[0]
    )

    result = await db.execute(select(Client).where(Client.email == email))
    client = result.scalar_one_or_none()

    if client is None:
        client = Client(name=name, email=email)
        db.add(client)
    elif not client.name:
        client.name = name

    await db.commit()
    await db.refresh(client)
    return client


@router.get("/cognito/status")
async def cognito_status():
    """Tell the frontend whether Cognito OAuth is wired up."""
    return {"enabled": cognito_configured()}


@router.post("/cognito/exchange")
async def cognito_exchange(req: CognitoExchangeRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a Hosted-UI auth code for an app session, upserting the client."""
    if not cognito_configured():
        raise HTTPException(503, "Cognito OAuth is not configured on the server")

    try:
        tokens = await exchange_code_for_tokens(req.code, req.redirect_uri)
        id_token = tokens.get("id_token")
        if not id_token:
            raise ValueError("No id_token returned from Cognito")
        claims = await verify_id_token(id_token)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 — surface a clean 401 to the client
        raise HTTPException(401, f"Google sign-in failed: {exc}")

    client = await _upsert_oauth_client(db, claims)
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
