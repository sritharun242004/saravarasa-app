"""
Sarvarasa Reactivation Payment (Razorpay)
Flow:
  1. POST /payment/create-order  → razorpay order_id
  2. Frontend completes Razorpay checkout
  3. POST /payment/verify         → validates signature, unlocks new challenge cycle
"""
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.core.security import get_current_client, require_owner
from app.models.client import Client, ClientStatus
from app.models.payment import PaymentTransaction

router = APIRouter(prefix="/payment", tags=["Payment"])

REACTIVATION_AMOUNT_PAISE = 29900  # ₹299 in paise
_is_dev_environment = settings.environment.lower() == "development"


class CreateOrderRequest(BaseModel):
    client_id: str


class VerifyPaymentRequest(BaseModel):
    client_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
async def create_order(
    req: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_client: str = Depends(get_current_client),
):
    """Create a Razorpay order for challenge reactivation."""
    require_owner(req.client_id, current_client)
    client = await db.get(Client, req.client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    if client.status != ClientStatus.LOCKED:
        raise HTTPException(400, "Reactivation is only available for locked accounts")

    # Try to create a Razorpay order
    try:
        import razorpay  # type: ignore
        rzp_client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )
        order = rzp_client.order.create({
            "amount": REACTIVATION_AMOUNT_PAISE,
            "currency": "INR",
            "receipt": f"sarvarasa_{req.client_id[:8]}",
        })
        order_id = order["id"]
    except Exception:
        # Razorpay not configured — only acceptable outside production, where
        # /payment/verify also refuses to skip signature verification.
        if not _is_dev_environment:
            raise HTTPException(503, "Payment processing is not configured")
        order_id = f"order_dev_{req.client_id[:8]}"

    txn = PaymentTransaction(
        client_id=req.client_id,
        razorpay_order_id=order_id,
        amount_inr=299.0,
        status="CREATED",
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)

    return {
        "order_id": order_id,
        "amount": REACTIVATION_AMOUNT_PAISE,
        "currency": "INR",
        "transaction_id": txn.id,
        "key_id": getattr(settings, "razorpay_key_id", ""),
    }


@router.post("/verify")
async def verify_payment(
    req: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_client: str = Depends(get_current_client),
):
    """Verify Razorpay signature and unlock new challenge cycle."""
    require_owner(req.client_id, current_client)
    client = await db.get(Client, req.client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    # Only trust an order we actually created and stored server-side — never
    # take the caller's word for which order/payment this is.
    result = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.razorpay_order_id == req.razorpay_order_id
        )
    )
    txn = result.scalar_one_or_none()
    if not txn or txn.client_id != req.client_id:
        raise HTTPException(404, "Payment order not found")
    if txn.status == "PAID":
        raise HTTPException(409, "This payment has already been verified")

    # "Dev mode" (skip signature check) is a server-side configuration fact —
    # never inferred from caller-supplied order_id/signature values. It is only
    # ever allowed outside production: shipping to prod with an unset/dev
    # Razorpay secret must fail closed, not silently accept unsigned payments.
    is_dev = settings.razorpay_key_secret in ("", "dev_secret")
    if is_dev and not _is_dev_environment:
        raise HTTPException(503, "Payment verification is not configured")

    if not is_dev:
        expected = hmac.new(
            settings.razorpay_key_secret.encode(),
            f"{req.razorpay_order_id}|{req.razorpay_payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, req.razorpay_signature):
            raise HTTPException(400, "Invalid payment signature")

    new_cycle = (client.challenge_cycle or 1) + 1
    txn.razorpay_payment_id = req.razorpay_payment_id
    txn.status = "PAID"
    txn.paid_at = datetime.now(timezone.utc)
    txn.cycle_unlocked = new_cycle

    # Unlock client
    client.status = ClientStatus.ACTIVE
    client.challenge_cycle = new_cycle

    await db.commit()

    return {
        "success": True,
        "message": "Payment verified. Your challenge has been reactivated!",
        "new_cycle": client.challenge_cycle,
        "client_status": client.status,
    }
