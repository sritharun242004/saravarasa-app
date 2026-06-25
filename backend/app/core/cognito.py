"""AWS Cognito OAuth helpers — Authorization-Code exchange + ID-token verification.

Everything is driven by app.config.settings (sourced from the environment); no
secrets are hardcoded here.
"""
from typing import Any, Optional

import httpx
from jose import jwt

from app.config import settings

# Cache the JSON Web Key Set for the user pool — it rarely changes.
_jwks_cache: Optional[dict] = None


def _issuer() -> str:
    return f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"


def _jwks_url() -> str:
    return f"{_issuer()}/.well-known/jwks.json"


def _token_url() -> str:
    return f"{settings.cognito_domain.rstrip('/')}/oauth2/token"


def cognito_configured() -> bool:
    return bool(
        settings.cognito_domain
        and settings.cognito_user_pool_id
        and settings.cognito_app_client_id
    )


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(_jwks_url())
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


async def exchange_code_for_tokens(code: str, redirect_uri: Optional[str] = None) -> dict[str, Any]:
    """Swap a Hosted-UI authorization code for Cognito tokens."""
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.cognito_app_client_id,
        "code": code,
        "redirect_uri": redirect_uri or settings.oauth_redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # Confidential app clients (with a secret) authenticate via HTTP Basic.
    auth = (
        (settings.cognito_app_client_id, settings.cognito_app_client_secret)
        if settings.cognito_app_client_secret
        else None
    )
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(_token_url(), data=data, headers=headers, auth=auth)
    if resp.status_code != 200:
        raise ValueError(f"Token exchange failed: {resp.status_code} {resp.text}")
    return resp.json()


async def verify_id_token(id_token: str) -> dict[str, Any]:
    """Verify a Cognito ID token's signature, audience and issuer; return its claims."""
    jwks = await _get_jwks()
    header = jwt.get_unverified_header(id_token)
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == header.get("kid")), None)
    if key is None:
        raise ValueError("Signing key not found in Cognito JWKS")

    claims = jwt.decode(
        id_token,
        key,
        algorithms=["RS256"],
        audience=settings.cognito_app_client_id,
        issuer=_issuer(),
        options={"verify_at_hash": False},
    )
    if claims.get("token_use") != "id":
        raise ValueError("Not an ID token")
    return claims
