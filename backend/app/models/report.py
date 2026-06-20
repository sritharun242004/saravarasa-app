from sqlalchemy import Column, String, Float, Integer, JSON, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ComplianceScore(Base):
    __tablename__ = "compliance_scores"

    client_id = Column(String, ForeignKey("clients.id"), primary_key=True)
    required_meals = Column(Integer, default=21)
    submitted_meals = Column(Integer, default=0)
    compliance_pct = Column(Float, default=0.0)
    status = Column(String, default="ACTIVE")  # PASSING / FAILED / COMPLETE
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="compliance_score")


class NutritionSummary(Base):
    __tablename__ = "nutrition_summaries"

    client_id = Column(String, ForeignKey("clients.id"), primary_key=True)
    total_calories = Column(Float, default=0.0)
    total_protein = Column(Float, default=0.0)
    total_carbs = Column(Float, default=0.0)
    total_fat = Column(Float, default=0.0)
    total_fiber = Column(Float, default=0.0)
    protein_pct = Column(Float, default=0.0)
    carb_pct = Column(Float, default=0.0)
    fat_pct = Column(Float, default=0.0)
    meal_pattern = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="nutrition_summary")


class ChallengeReport(Base):
    __tablename__ = "challenge_reports"

    client_id = Column(String, ForeignKey("clients.id"), primary_key=True)
    compliance_score = Column(Float, default=0.0)
    completed_days = Column(Integer, default=0)
    qualification_status = Column(String, nullable=True)   # QUALIFIED / SECOND_CHANCE / LOCKED
    eligibility_score = Column(Float, default=0.0)
    eligibility_band = Column(String, nullable=True)
    meal_pattern = Column(String, nullable=True)
    # Sarvarasa food awareness fields
    food_observations = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    improvement_areas = Column(JSON, default=list)
    action_plan = Column(JSON, default=list)
    wholesome_plate_tips = Column(JSON, default=list)
    food_pattern_summary = Column(JSON, default=dict)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # LLM-generated fields (added after initial schema)
    commitment_level = Column(String, nullable=True)          # HIGH / MODERATE / LOW
    commitment_analysis = Column(Text, nullable=True)         # narrative about seriousness
    food_recommendations = Column(JSON, nullable=True)        # list of {food_name, category, reason, ...}
    llm_insights = Column(JSON, nullable=True)                # personalized_insights + seriousness_indicators
    llm_summary = Column(Text, nullable=True)                 # overall narrative
    llm_generated_at = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client", back_populates="challenge_report")
