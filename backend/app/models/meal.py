from sqlalchemy import Column, String, Float, JSON, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Meal(Base):
    __tablename__ = "meals"

    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)

    # Detected foods
    detected_foods = Column(JSON, nullable=False, default=list)

    # Macros
    total_calories = Column(Float, default=0)
    protein_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    fiber_g = Column(Float, default=0)

    # Micronutrients (JSON blob)
    micronutrients = Column(JSON, default=dict)

    # Health scores
    health_scores = Column(JSON, default=dict)

    # User answers to questions
    question_answers = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(String, primary_key=True, default=gen_uuid)
    image_url = Column(String, nullable=True)
    detected_foods = Column(JSON, default=list)
    questions = Column(JSON, default=list)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
