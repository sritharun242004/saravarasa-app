"""
Phase-2 embedding generator (psycopg2, sync, batch reconnect).
Fills embedding vectors for all foods that have embedding IS NULL.

Run after adding OPENROUTER_API_KEY to backend/.env:
    cd backend
    python scripts/generate_embeddings.py
"""
import sys, os, re, time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import psycopg2
from openai import OpenAI

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_KEY or OPENROUTER_KEY == "your-openrouter-api-key-here":
    print("ERROR: Set OPENROUTER_API_KEY in backend/.env first.")
    sys.exit(1)

client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)

DB_URL_RAW = os.environ.get("DATABASE_URL", "")
MODEL      = "text-embedding-3-small"
RATE_DELAY = 0.12
BATCH_SIZE = 50

from app.services.embeddings.food_embedding import (
    build_food_embedding_text, get_food_knowledge,
)


def _to_dsn(url: str) -> str:
    url = url.replace("postgresql+asyncpg://", "").replace("postgresql://", "")
    m = re.match(r"([^:]+):([^@]+)@([^/]+)/([^?]+)", url)
    if not m:
        raise ValueError(f"Cannot parse DATABASE_URL: {url}")
    user, pwd, host, db = m.groups()
    return f"host={host} dbname={db} user={user} password={pwd} sslmode=require"

DSN = _to_dsn(DB_URL_RAW)


def new_conn():
    return psycopg2.connect(DSN, connect_timeout=30)


def embed(text: str) -> list[float] | None:
    try:
        result = client.embeddings.create(model=MODEL, input=text)
        return result.data[0].embedding
    except Exception as e:
        print(f"    embed error: {e}")
        return None


def vec_str(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"


def main():
    print("=" * 55)
    print("NutriLens — Phase-2 Embedding Generator")
    print("=" * 55)

    conn = new_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT f.id, f.name, f.canonical_name,
                   c.name AS category, r.name AS region, m.name AS meal_type
            FROM foods f
            LEFT JOIN categories c  ON f.category_id  = c.id
            LEFT JOIN regions r     ON f.region_id     = r.id
            LEFT JOIN meal_types m  ON f.meal_type_id  = m.id
            WHERE f.embedding IS NULL
            ORDER BY f.created_at
        """)
        rows = cur.fetchall()
    conn.close()

    total = len(rows)
    print(f"Foods needing embeddings: {total}")
    if total == 0:
        print("All foods already have embeddings. Done.")
        return

    done = 0
    for batch_start in range(0, total, BATCH_SIZE):
        batch = rows[batch_start : batch_start + BATCH_SIZE]
        conn = new_conn()

        with conn.cursor() as cur:
            for row in batch:
                food_id, name, canonical, category, region, meal_type = row
                nl = name.lower()
                know = get_food_knowledge(nl)

                text = build_food_embedding_text(
                    name=name,
                    canonical_name=canonical,
                    category=category,
                    region=region,
                    meal_type=meal_type,
                    ingredients=know.get("ingredients", []),
                    aliases=know.get("aliases", []),
                    description=know.get("description", ""),
                )

                vec = embed(text)
                if vec:
                    cur.execute(
                        "UPDATE foods SET embedding = %s::vector WHERE id = %s",
                        (vec_str(vec), food_id)
                    )
                time.sleep(RATE_DELAY)
                done += 1

        conn.commit()
        conn.close()
        print(f"  {done}/{total} embeddings generated…")

    print(f"\nDone — {done} embeddings written to Neon.")
    print("Semantic search is now active.")
    print("=" * 55)


if __name__ == "__main__":
    main()
