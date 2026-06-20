import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class FoodAlias(Base):
    """Keyword-level alias→canonical mapping used by food_pattern_engine seed."""
    __tablename__ = "food_keyword_aliases"

    id = Column(String, primary_key=True, default=gen_uuid)
    alias = Column(String, nullable=False, unique=True, index=True)   # e.g. "idly", "chai", "soru"
    canonical = Column(String, nullable=False)                         # e.g. "idli", "tea", "rice"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
