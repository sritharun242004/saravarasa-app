import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class FoodAliasSearch(Base):
    """Aliases for structured food search (trigram-indexed). Table: food_aliases."""
    __tablename__ = "food_aliases"

    id = Column(String, primary_key=True, default=gen_uuid)
    food_id = Column(String, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False, index=True)
    alias_name = Column(Text, nullable=False)

    food = relationship("Food", back_populates="aliases")
