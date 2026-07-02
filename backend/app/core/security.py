import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Header, HTTPException
from jose import JWTError, jwt
from app.config import settings

ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30
_ITERATIONS = 260_000


def hash_password(plain: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), _ITERATIONS)
    return f"pbkdf2$sha256${salt}${h.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    try:
        _, algo, salt, hashed = stored.split("$")
        h = hashlib.pbkdf2_hmac(algo, plain.encode(), salt.encode(), _ITERATIONS)
        return secrets.compare_digest(h.hex(), hashed)
    except Exception:
        return False


def create_token(client_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": client_id, "exp": expire}, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def require_admin(authorization: Optional[str] = Header(None)) -> str:
    """FastAPI dependency — allow only the configured admin token (sub == admin email)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Admin authentication required")
    sub = decode_token(authorization.removeprefix("Bearer "))
    if not sub or not settings.admin_email or sub.lower() != settings.admin_email.lower():
        raise HTTPException(403, "Admin access required")
    return sub


def get_current_client(authorization: Optional[str] = Header(None)) -> str:
    """FastAPI dependency — resolves the client_id from a valid Bearer token.

    Every client-facing route must use this (not a caller-supplied client_id)
    to decide *whose* data is being read or written.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    sub = decode_token(authorization.removeprefix("Bearer "))
    if not sub:
        raise HTTPException(401, "Invalid or expired token")
    return sub


def require_owner(client_id: str, current_client: str) -> None:
    """Raise 403 unless the authenticated caller matches the resource's client_id."""
    if client_id != current_client:
        raise HTTPException(403, "Not authorized for this client")
