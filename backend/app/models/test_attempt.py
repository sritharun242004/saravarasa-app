import enum
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class TestType(str, enum.Enum):
    MCQ = "MCQ"
    DESCRIPTIVE = "DESCRIPTIVE"


class TestStatus(str, enum.Enum):
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(String, primary_key=True, default=gen_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    test_type = Column(String, nullable=False)  # MCQ or DESCRIPTIVE
    challenge_cycle = Column(Integer, default=1)  # Track which cycle this was attempted in
    score = Column(Float, nullable=True)  # 0-100
    status = Column(String, default=TestStatus.LOCKED)
    answers = Column(JSON, nullable=True)  # Store answers as JSON
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", foreign_keys=[client_id])


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=gen_uuid)
    test_type = Column(String, nullable=False)  # MCQ or DESCRIPTIVE
    question_text = Column(Text, nullable=False)
    order = Column(Integer, nullable=True)  # Question order/sequence

    # MCQ specific fields
    options = Column(JSON, nullable=True)  # {a: "option", b: "option", c: "option", d: "option"}
    correct_answer = Column(String, nullable=True)  # a, b, c, or d

    # Shared
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
