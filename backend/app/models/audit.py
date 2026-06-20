import uuid
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class LifestyleAudit(Base):
    __tablename__ = "lifestyle_audits"

    id = Column(String, primary_key=True, default=gen_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, unique=True, index=True)

    # Basic Profile
    city = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    cooking_at_home = Column(Boolean, nullable=True)

    # Sleep
    sleep_hours = Column(String, nullable=True)       # "less_than_6", "6_to_7", "7_to_8", "more_than_8"
    sleep_quality = Column(String, nullable=True)     # "poor", "average", "good"
    wake_time = Column(String, nullable=True)

    # Food Habits
    meals_per_day = Column(String, nullable=True)     # "1_to_2", "3", "4_or_more"
    breakfast_habit = Column(String, nullable=True)   # "always", "sometimes", "rarely", "never"
    water_intake = Column(String, nullable=True)      # "less_than_1L", "1_to_2L", "more_than_2L"
    outside_food_frequency = Column(String, nullable=True)  # "daily", "few_times_week", "rarely"
    sugary_beverage_frequency = Column(String, nullable=True)
    processed_food_frequency = Column(String, nullable=True)

    # Movement
    activity_level = Column(String, nullable=True)   # "sedentary", "lightly_active", "moderately_active", "very_active"
    exercise_frequency = Column(String, nullable=True)

    # Stress
    stress_level = Column(String, nullable=True)     # "low", "moderate", "high"
    stress_eating = Column(String, nullable=True)    # "yes", "sometimes", "no"

    # Digestive Health
    digestion_issues = Column(Boolean, nullable=True)
    digestion_notes = Column(Text, nullable=True)
    bowel_regularity = Column(String, nullable=True) # "regular", "irregular"

    # Additional notes
    health_goals = Column(Text, nullable=True)
    dietary_restrictions = Column(Text, nullable=True)

    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="lifestyle_audit")
