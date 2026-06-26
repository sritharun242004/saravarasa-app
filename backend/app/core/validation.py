"""Shared input validation/normalization for auth and profile flows.

Keeps signup, login and profile-update consistent (email casing, phone format,
password strength) so the same rules apply everywhere.
"""
import re
from typing import Optional

from fastapi import HTTPException
from email_validator import (
    validate_email as _ev_validate,
    EmailNotValidError,
    EmailSyntaxError,
    EmailUndeliverableError,
)

# A short-timeout DNS resolver so the signup request never hangs on a slow lookup.
try:
    import dns.resolver as _dns_resolver

    _RESOLVER = _dns_resolver.Resolver()
    _RESOLVER.timeout = 5
    _RESOLVER.lifetime = 5
except Exception:  # pragma: no cover - dnspython missing
    _RESOLVER = None


def normalize_email(email: str) -> str:
    """Lower-case + trim so email uniqueness/login is case-insensitive."""
    return (email or "").strip().lower()


def validate_email_deliverable(email: str) -> str:
    """Validate format AND that the email's domain actually exists / can receive mail.

    Rejects fake or mistyped domains (e.g. 'foo@doesnotexist123.com'). Returns the
    normalized lowercase address. Fails OPEN on transient DNS errors so a flaky
    lookup never blocks a genuine user.

    Note: this confirms the *domain* can receive mail, not that the specific mailbox
    exists — only a confirmation email/OTP can prove that.
    """
    raw = (email or "").strip()
    if not raw:
        raise HTTPException(400, "Email is required")

    # 1) Syntax — always enforced.
    try:
        result = _ev_validate(raw, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(400, "Please enter a valid email address")

    normalized = result.normalized.lower()

    # 2) Deliverability (domain exists + has mail records). Best-effort.
    try:
        _ev_validate(normalized, check_deliverability=True, dns_resolver=_RESOLVER)
    except EmailUndeliverableError as exc:
        msg = str(exc).lower()
        # Permanent failures → reject. Transient (timeout/temporary) → allow.
        if any(s in msg for s in ("does not exist", "does not accept email", "no usable", "without a mail")):
            raise HTTPException(
                400, "That email's domain can't receive mail. Please use a real email address."
            )
    except EmailSyntaxError:
        raise HTTPException(400, "Please enter a valid email address")
    except EmailNotValidError:
        # Unknown validation issue — don't block a real user over a DNS hiccup.
        pass

    return normalized


def normalize_phone(phone: Optional[str], required: bool = False) -> Optional[str]:
    """Validate and normalize to a bare 10-digit Indian mobile number.

    Accepts inputs like '+91 98765 43210', '098765-43210', '9876543210' and
    stores them as '9876543210'. Rejects anything that isn't a valid 10-digit
    mobile (must start 6-9).
    """
    if not phone or not phone.strip():
        if required:
            raise HTTPException(400, "Phone number is required")
        return None

    digits = re.sub(r"\D", "", phone)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) != 10 or digits[0] not in "6789":
        raise HTTPException(400, "Enter a valid 10-digit mobile number")
    return digits


def validate_password(password: str) -> None:
    """Enforce a sensible minimum strength (length + letter + number)."""
    if not password or len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if len(password) > 128:
        raise HTTPException(400, "Password is too long")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(400, "Password must include at least one letter and one number")


def validate_name(name: str) -> str:
    cleaned = (name or "").strip()
    if len(cleaned) < 2:
        raise HTTPException(400, "Please enter your full name")
    return cleaned
