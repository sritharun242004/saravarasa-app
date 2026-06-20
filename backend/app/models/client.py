import enum
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class ClientStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    QUALIFIED = "QUALIFIED"
    SECOND_CHANCE = "SECOND_CHANCE"
    LOCKED = "LOCKED"
    # legacy
    PASSED = "PASSED"
    FAILED = "FAILED"
    ENROLLED = "ENROLLED"


class ChallengeBatch(Base):
    __tablename__ = "challenge_batches"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    capacity = Column(Integer, default=100)

    clients = relationship("Client", back_populates="batch")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    goal = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    password_hash = Column(String, nullable=True)
    batch_id = Column(String, ForeignKey("challenge_batches.id"), nullable=True)
    status = Column(String, default=ClientStatus.ACTIVE)
    audit_completed = Column(Boolean, default=False)
    challenge_cycle = Column(Integer, default=1)  # 1 = first week, 2 = second chance
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    batch = relationship("ChallengeBatch", back_populates="clients")
    meal_logs = relationship("MealLog", back_populates="client")
    compliance_score = relationship("ComplianceScore", back_populates="client", uselist=False)
    nutrition_summary = relationship("NutritionSummary", back_populates="client", uselist=False)
    challenge_report = relationship("ChallengeReport", back_populates="client", uselist=False)
    lifestyle_audit = relationship("LifestyleAudit", back_populates="client", uselist=False)
    challenge_attempts = relationship("ChallengeAttempt", back_populates="client")
    payment_transactions = relationship("PaymentTransaction", back_populates="client")
