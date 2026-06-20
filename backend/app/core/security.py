import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
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
