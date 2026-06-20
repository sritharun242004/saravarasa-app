"""Alembic environment — sync psycopg2 against Neon PostgreSQL."""
import os
import re
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from app.database import Base
import app.models  # noqa: F401 — registers all ORM models

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_raw_url = os.environ["DATABASE_URL"]
# Normalise to psycopg2 (sync) driver
_db_url = (
    _raw_url
    .replace("postgresql+asyncpg://", "postgresql://")
    .replace("?ssl=require", "")
    .replace("?sslmode=require", "")
    .replace("&channel_binding=require", "")
    .replace("?channel_binding=require", "")
)
# Append sslmode so psycopg2 connects securely to Neon
DB_URL = _db_url + ("&" if "?" in _db_url else "?") + "sslmode=require"


def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(DB_URL, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
