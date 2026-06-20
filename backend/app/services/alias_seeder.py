"""
Seed the food_aliases table with common South Indian / Indian food name aliases.
Run once on startup if the table is empty.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

SEED_ALIASES = [
    # Tamil/South Indian regional names
    ("idly", "idli"),
    ("idlies", "idli"),
    ("dosa", "dosa"),
    ("dosai", "dosa"),
    ("sadham", "rice"),
    ("soru", "rice"),
    ("sadam", "rice"),
    ("keerai", "spinach"),
    ("thayir", "curd"),
    ("thayir sadam", "curd rice"),
    ("chai", "tea"),
    ("chaa", "tea"),
    ("kaapi", "coffee"),
    ("kaapee", "coffee"),
    ("paal", "milk"),
    ("meen", "fish"),
    ("kozhi", "chicken"),
    ("mutton curry", "mutton"),
    ("kuzhambu", "curry"),
    ("kolambu", "curry"),
    ("rasam", "rasam"),
    ("mor", "buttermilk"),
    ("moru", "buttermilk"),
    ("payasam", "kheer"),
    ("vadai", "vada"),
    ("bondaa", "bonda"),
    ("poori", "puri"),
    ("chapathi", "chapati"),
    # Hindi / North Indian
    ("aloo", "potato"),
    ("sabzi", "vegetable curry"),
    ("dal", "lentil soup"),
    ("dhal", "lentil soup"),
    ("daal", "lentil soup"),
    ("roti", "chapati"),
    ("phulka", "chapati"),
    ("bhaat", "rice"),
    ("cheera", "spinach"),
    ("paneer", "paneer"),
    ("curd", "curd"),
    ("dahi", "curd"),
    ("chaas", "buttermilk"),
    ("lassi", "lassi"),
    # Beverages
    ("milk tea", "tea"),
    ("green tea", "tea"),
    ("masala chai", "tea"),
    ("filter coffee", "coffee"),
    ("black coffee", "coffee"),
    # Common short forms
    ("pb", "peanut butter"),
    ("oats", "oatmeal"),
    ("pb&j", "peanut butter sandwich"),
]


async def seed_aliases(db: AsyncSession) -> None:
    from app.models.food_alias import FoodAlias
    count_r = await db.execute(select(func.count(FoodAlias.id)))
    count = count_r.scalar() or 0
    if count > 0:
        return  # already seeded

    for alias, canonical in SEED_ALIASES:
        db.add(FoodAlias(alias=alias.lower().strip(), canonical=canonical.lower().strip()))
    await db.commit()
