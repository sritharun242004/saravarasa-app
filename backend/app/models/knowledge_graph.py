"""
Knowledge Graph SQLAlchemy models.
foods → categories, regions, meal_types
foods → food_aliases (name variants)
foods → food_ingredients → ingredients
foods → food_nutrients → nutrients
"""
import uuid
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database import Base


def _uuid():
    return str(uuid.uuid4())


# ── Lookup tables ─────────────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    foods = relationship("Food", back_populates="category")


class Region(Base):
    __tablename__ = "regions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name = Column(String(120), nullable=False, unique=True)
    country = Column(String(80), default="India")

    foods = relationship("Food", back_populates="region")


class MealType(Base):
    __tablename__ = "meal_types"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name = Column(String(80), nullable=False, unique=True)  # Breakfast, Lunch, Dinner, Snack

    foods = relationship("Food", back_populates="meal_type")


# ── Core food node ─────────────────────────────────────────────────────────────

class Food(Base):
    __tablename__ = "foods"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    indb_code = Column(String(20), unique=True, nullable=True, index=True)
    name = Column(Text, nullable=False)
    canonical_name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    category_id = Column(UUID(as_uuid=False), ForeignKey("categories.id"), nullable=True)
    region_id = Column(UUID(as_uuid=False), ForeignKey("regions.id"), nullable=True)
    meal_type_id = Column(UUID(as_uuid=False), ForeignKey("meal_types.id"), nullable=True)

    # 768-dim vector from Gemini text-embedding-004
    embedding = Column(Vector(768), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="foods")
    region = relationship("Region", back_populates="foods")
    meal_type = relationship("MealType", back_populates="foods")
    aliases = relationship("FoodAlias", back_populates="food", cascade="all, delete-orphan")
    food_nutrients = relationship("FoodNutrient", back_populates="food", cascade="all, delete-orphan")
    food_ingredients = relationship("FoodIngredient", back_populates="food", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_foods_embedding", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


class FoodAlias(Base):
    __tablename__ = "food_aliases"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    food_id = Column(UUID(as_uuid=False), ForeignKey("foods.id", ondelete="CASCADE"), nullable=False, index=True)
    alias = Column(Text, nullable=False)
    language = Column(String(20), default="en")   # en, ta, te, kn, hi, ml
    confidence = Column(Float, default=1.0)

    food = relationship("Food", back_populates="aliases")

    __table_args__ = (UniqueConstraint("food_id", "alias", name="uq_food_alias"),)


# ── Ingredients ───────────────────────────────────────────────────────────────

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name = Column(String(200), nullable=False, unique=True)
    embedding = Column(Vector(768), nullable=True)

    food_ingredients = relationship("FoodIngredient", back_populates="ingredient")


class FoodIngredient(Base):
    __tablename__ = "food_ingredients"

    food_id = Column(UUID(as_uuid=False), ForeignKey("foods.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id = Column(UUID(as_uuid=False), ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    quantity_g = Column(Float, nullable=True)       # grams per 100g of food
    is_primary = Column(String(5), default="true")  # main ingredient flag

    food = relationship("Food", back_populates="food_ingredients")
    ingredient = relationship("Ingredient", back_populates="food_ingredients")


# ── Nutrients ─────────────────────────────────────────────────────────────────

class Nutrient(Base):
    __tablename__ = "nutrients"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name = Column(String(100), nullable=False, unique=True)
    unit = Column(String(20), nullable=False)         # g, mg, μg, kcal, kJ
    category = Column(String(50), nullable=True)      # macro, mineral, vitamin, energy
    description = Column(Text, nullable=True)

    food_nutrients = relationship("FoodNutrient", back_populates="nutrient")


class FoodNutrient(Base):
    __tablename__ = "food_nutrients"

    food_id = Column(UUID(as_uuid=False), ForeignKey("foods.id", ondelete="CASCADE"), primary_key=True)
    nutrient_id = Column(UUID(as_uuid=False), ForeignKey("nutrients.id", ondelete="CASCADE"), primary_key=True)
    value_per_100g = Column(Float, nullable=False, default=0.0)

    food = relationship("Food", back_populates="food_nutrients")
    nutrient = relationship("Nutrient", back_populates="food_nutrients")
