import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"

    id = Column(String, primary_key=True, default=gen_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    cycle = Column(Integer, nullable=False, default=1)     # 1 = first, 2 = second chance
    compliance_pct = Column(Float, nullable=True)
    completed_days = Column(Integer, default=0)
    status = Column(String, default="ACTIVE")              # ACTIVE / QUALIFIED / FAILED
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client", back_populates="challenge_attempts")
