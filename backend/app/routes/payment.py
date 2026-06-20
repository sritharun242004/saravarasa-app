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
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.models.client import Client, ClientStatus
from app.models.payment import PaymentTransaction

router = APIRouter(prefix="/payment", tags=["Payment"])

REACTIVATION_AMOUNT_PAISE = 29900  # ₹299 in paise


class CreateOrderRequest(BaseModel):
    client_id: str


class VerifyPaymentRequest(BaseModel):
    client_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
async def create_order(req: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    """Create a Razorpay order for challenge reactivation."""
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
        # Razorpay not configured — return mock order for dev
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
async def verify_payment(req: VerifyPaymentRequest, db: AsyncSession = Depends(get_db)):
    """Verify Razorpay signature and unlock new challenge cycle."""
    client = await db.get(Client, req.client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    key_secret = getattr(settings, "razorpay_key_secret", "dev_secret")
    is_dev = key_secret == "dev_secret" or req.razorpay_order_id.startswith("order_dev_")

    if not is_dev:
        expected = hmac.new(
            key_secret.encode(),
            f"{req.razorpay_order_id}|{req.razorpay_payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        if expected != req.razorpay_signature:
            raise HTTPException(400, "Invalid payment signature")

    # Find and update the pending transaction
    from sqlalchemy import select
    result = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.razorpay_order_id == req.razorpay_order_id
        )
    )
    txn = result.scalar_one_or_none()
    if txn:
        txn.razorpay_payment_id = req.razorpay_payment_id
        txn.status = "PAID"
        txn.paid_at = datetime.now(timezone.utc)
        new_cycle = (client.challenge_cycle or 1) + 1
        txn.cycle_unlocked = new_cycle

    # Unlock client
    client.status = ClientStatus.ACTIVE
    client.challenge_cycle = (client.challenge_cycle or 1) + 1

    await db.commit()

    return {
        "success": True,
        "message": "Payment verified. Your challenge has been reactivated!",
        "new_cycle": client.challenge_cycle,
        "client_status": client.status,
    }
