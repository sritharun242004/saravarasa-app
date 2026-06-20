import ssl
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Neon (and any TLS-required Postgres) needs an SSL context passed via connect_args.
# asyncpg ignores sslmode/channel_binding in the URL, so we handle it here.
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

# Strip query params that asyncpg doesn't understand before passing to the engine.
_db_url = (
    settings.database_url
    .replace("?sslmode=require", "")
    .replace("?ssl=require", "")
    .replace("&channel_binding=require", "")
    .replace("?channel_binding=require", "")
)

engine = create_async_engine(
    _db_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={"ssl": _ssl_ctx},
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    import app.models  # noqa: F401 — registers all ORM models with Base.metadata
    async with engine.begin() as conn:
        # Enable trigram extension before creating tables that depend on it.
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)
        # GIN trigram indexes for sub-100 ms food search.
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_foods_canonical_trgm
            ON foods USING gin (LOWER(canonical_name) gin_trgm_ops)
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_food_aliases_name_trgm
            ON food_aliases USING gin (LOWER(alias_name) gin_trgm_ops)
        """))
