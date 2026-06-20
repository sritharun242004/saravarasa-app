import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class MealFood(Base):
    """Structured food entries linked to a meal log."""
    __tablename__ = "meal_foods"

    id = Column(String, primary_key=True, default=gen_uuid)
    meal_log_id = Column(String, ForeignKey("meal_logs.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id = Column(String, ForeignKey("foods.id"), nullable=True)   # nullable: food may be unrecognised
    food_name = Column(String, nullable=True)                  # denormalised for display without a join
    quantity = Column(Float, nullable=False, default=100.0)   # in grams (normalised)
    unit = Column(String(50), default="g")                    # display unit (piece, cup, g …)
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    food = relationship("Food", back_populates="meal_foods")
