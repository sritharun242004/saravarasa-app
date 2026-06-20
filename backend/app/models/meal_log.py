import enum
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class MealType(str, enum.Enum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    SNACK = "SNACK"


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)   # 1–7
    meal_type = Column(String, nullable=False)      # BREAKFAST / LUNCH / DINNER / SNACK
    meal_text = Column(Text, nullable=False)        # "3 idli, sambar, tea"
    image_url = Column(String, nullable=True)       # uploaded image path
    food_pattern_tags = Column(JSON, default=list)  # ["PROTEIN_PRESENT", "VEGETABLE_PRESENT", ...]
    challenge_cycle = Column(Integer, default=1)    # 1 = first attempt, 2 = second chance
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="meal_logs")
