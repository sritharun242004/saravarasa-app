import uuid
from sqlalchemy import Column, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Food(Base):
    __tablename__ = "foods"

    id = Column(String, primary_key=True, default=gen_uuid)
    food_code = Column(String(50), nullable=True, index=True)
    canonical_name = Column(Text, nullable=False)
    search_text = Column(Text, nullable=True)       # canonical_name + all alias names
    energy_kcal = Column(Float, default=0.0)        # per 100 g
    protein_g = Column(Float, default=0.0)
    carb_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)
    serving_unit = Column(String(50), nullable=True, default="g")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    aliases = relationship("FoodAliasSearch", back_populates="food", cascade="all, delete-orphan")
    meal_foods = relationship("MealFood", back_populates="food")
