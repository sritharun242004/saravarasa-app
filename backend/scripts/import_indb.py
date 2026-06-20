"""
INDB 2024.11 → PostgreSQL Import (trigram-search edition)
==========================================================
No embeddings. No pgvector. Pure SQL + pg_trgm.

Run once from the backend directory:
    python scripts/import_indb.py

Idempotent — uses ON CONFLICT DO NOTHING.
Reconnects every BATCH_SIZE rows to survive Neon's connection timeout.
"""
import sys, os, re, uuid
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pandas as pd
import psycopg2

# ── Config ────────────────────────────────────────────────────────────────────
DB_URL_RAW = os.environ.get("DATABASE_URL", "")
INDB_PATH  = Path(os.environ.get("INDB_FILE_PATH",
             ROOT / ".." / "data" / "Anuvaad_INDB_2024.11.xlsx"))
BATCH_SIZE = 50


def _to_dsn(url: str) -> str:
    url = (url
           .replace("postgresql+asyncpg://", "")
           .replace("postgresql://", ""))
    m = re.match(r"([^:]+):([^@]+)@([^/]+)/([^?]+)", url)
    if not m:
        raise ValueError(f"Cannot parse DATABASE_URL: {url}")
    user, pwd, host, db = m.groups()
    return f"host={host} dbname={db} user={user} password={pwd} sslmode=require"


DSN = _to_dsn(DB_URL_RAW)


def new_conn():
    return psycopg2.connect(DSN, connect_timeout=30)


# ── Nutrient columns ──────────────────────────────────────────────────────────
# Maps (excel_column, new_column) for the four main macros we store inline.
MACRO_COLS = [
    ("energy_kcal", "energy_kcal"),
    ("protein_g",   "protein_g"),
    ("carb_g",      "carb_g"),
    ("fibre_g",     "fiber_g"),   # INDB uses 'fibre_g', our table uses 'fiber_g'
    ("fat_g",       "fat_g"),
]


def _safe(val) -> float:
    try:
        f = float(val)
        return 0.0 if f != f else f   # NaN → 0
    except Exception:
        return 0.0


# ── Alias knowledge base ──────────────────────────────────────────────────────
# Hardcoded regional / spelling aliases for common Indian foods.
ALIAS_BANK = {
    "idli":          ["idly", "idlies", "steamed rice cake"],
    "dosa":          ["dosai", "dose", "thosai"],
    "uttapam":       ["uthappam", "oothapam", "uttapam"],
    "upma":          ["uppuma", "upittu"],
    "pongal":        ["ven pongal", "venpongal", "khichdi rice"],
    "appam":         ["aappam", "palappam"],
    "idiyappam":     ["string hoppers", "noolappam"],
    "puttu":         ["pittu"],
    "pesarattu":     ["green moong dosa"],
    "rice":          ["sadham", "soru", "sadam", "bhaat", "chawal", "annam"],
    "sambar":        ["sambhar", "sambaru"],
    "rasam":         ["rasam soup", "pepper water", "tomato rasam"],
    "curd":          ["dahi", "thayir", "thayiru", "yogurt", "yoghurt", "mosaru"],
    "curd rice":     ["thayir sadam", "dahi rice", "yogurt rice"],
    "buttermilk":    ["mor", "moru", "chaas", "majjiga", "lassi salted"],
    "dal":           ["dhal", "daal", "lentil soup", "parippu curry"],
    "chapati":       ["roti", "phulka", "chapathi"],
    "paratha":       ["parantha", "parota", "malabar parota"],
    "puri":          ["poori"],
    "tea":           ["chai", "chaa", "garam chai", "milk tea", "masala chai"],
    "coffee":        ["kaapi", "kaapee", "filter coffee", "south indian coffee"],
    "milk":          ["paal", "doodh"],
    "chicken":       ["kozhi", "murgh"],
    "mutton":        ["lamb", "goat meat", "aatukal"],
    "fish":          ["meen", "machli"],
    "egg":           ["muttai", "anda", "boiled egg", "omelette"],
    "paneer":        ["cottage cheese", "fresh cheese"],
    "potato":        ["aloo", "urulaikizhangu"],
    "spinach":       ["keerai", "palak", "cheera"],
    "banana":        ["vazhaipazham", "kela"],
    "coconut":       ["thengai", "nariyal"],
    "groundnut":     ["peanut", "moongphali", "nilakadalai"],
    "cashew":        ["kaju", "mundhiri"],
    "lemon":         ["lime", "elumichai", "nimbu"],
    "mango":         ["maanga", "aam", "raw mango"],
    "tamarind":      ["puli", "imli"],
    "mustard":       ["rai", "kadugu"],
    "turmeric":      ["haldi", "manjal"],
    "cumin":         ["jeera", "jeerakam"],
    "oatmeal":       ["oats", "rolled oats", "porridge"],
    "ragi":          ["finger millet", "nachni", "kezhvaragu"],
    "jowar":         ["sorghum", "cholam"],
    "bajra":         ["pearl millet", "kambu"],
    "wheat":         ["whole wheat", "atta"],
    "brown rice":    ["unpolished rice"],
    "poha":          ["flattened rice", "aval", "avalakki"],
    "biryani":       ["biriyani", "biryani rice"],
    "khichdi":       ["khichri", "dal khichdi"],
    "lassi":         ["sweet lassi", "mango lassi"],
    "halwa":         ["halva"],
    "payasam":       ["kheer", "payasam sweet"],
    "vada":          ["vadai", "medu vada", "uzhunnu vada"],
    "bonda":         ["bondaa", "aloo bonda"],
    "samosa":        ["samusa"],
    "pakora":        ["pakoda", "bhajia"],
    "chutney":       ["dip", "sauce"],
    "pickle":        ["achar", "urugai"],
}


def _extract_parenthetical_aliases(name: str):
    """'Hot tea (Garam Chai)' → canonical='Hot tea', aliases=['garam chai']."""
    m = re.search(r"\(([^)]+)\)", name)
    if not m:
        return name.strip(), []
    canonical = name[:m.start()].strip()
    inner = m.group(1).strip().lower()
    parts = [p.strip() for p in re.split(r"[,/]", inner) if p.strip()]
    return canonical, parts


def _infer_serving_unit(name: str) -> str:
    n = name.lower()
    liquid_words = ("soup", "rasam", "sambar", "dal", "broth", "juice", "milk",
                    "tea", "coffee", "lassi", "buttermilk", "chai", "water")
    piece_words  = ("idli", "dosa", "roti", "chapati", "chapathi", "phulka",
                    "puri", "paratha", "parota", "egg", "vada", "vadai",
                    "bonda", "pakora", "samosa", "modak", "kozhukattai")
    cup_words    = ("rice", "biryani", "khichdi", "upma", "pongal", "poha",
                    "oatmeal", "oats", "cereals")
    for w in liquid_words:
        if w in n:
            return "cup"
    for w in piece_words:
        if w in n:
            return "piece"
    for w in cup_words:
        if w in n:
            return "cup"
    return "g"


def _build_aliases(canonical: str, extra: list[str]) -> list[str]:
    """Return de-duped lowercase alias list for a food."""
    cl = canonical.lower().strip()
    seen = {cl}
    result = []

    # 1. From parenthetical extraction
    for a in extra:
        a = a.lower().strip()
        if a and a not in seen:
            seen.add(a)
            result.append(a)

    # 2. From hardcoded bank (check if canonical matches a key)
    for key, aliases in ALIAS_BANK.items():
        if key in cl or cl in key:
            for a in aliases:
                a = a.lower().strip()
                if a and a not in seen:
                    seen.add(a)
                    result.append(a)
            break

    # 3. Individual words from multi-word names (only if ≥2 words)
    words = [w for w in cl.split() if len(w) > 3]
    if len(words) >= 2:
        for w in words:
            if w not in seen:
                seen.add(w)
                result.append(w)

    return result


# ── Schema setup ──────────────────────────────────────────────────────────────

def setup_schema(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id           TEXT PRIMARY KEY,
                food_code    VARCHAR(50),
                canonical_name TEXT NOT NULL,
                search_text  TEXT,
                energy_kcal  FLOAT DEFAULT 0,
                protein_g    FLOAT DEFAULT 0,
                carb_g       FLOAT DEFAULT 0,
                fat_g        FLOAT DEFAULT 0,
                fiber_g      FLOAT DEFAULT 0,
                serving_unit TEXT,
                created_at   TIMESTAMPTZ DEFAULT now()
            )
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_foods_food_code
            ON foods (food_code) WHERE food_code IS NOT NULL
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS food_aliases (
                id        TEXT PRIMARY KEY,
                food_id   TEXT NOT NULL REFERENCES foods(id) ON DELETE CASCADE,
                alias_name TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_food_aliases_food_alias
            ON food_aliases (food_id, alias_name)
        """)

        # Trigram indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_foods_canonical_trgm
            ON foods USING gin (LOWER(canonical_name) gin_trgm_ops)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_food_aliases_name_trgm
            ON food_aliases USING gin (LOWER(alias_name) gin_trgm_ops)
        """)

        # meal_foods (created by SQLAlchemy ORM but also ensure it exists)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meal_foods (
                id          TEXT PRIMARY KEY,
                meal_log_id TEXT NOT NULL REFERENCES meal_logs(id) ON DELETE CASCADE,
                food_id     TEXT NOT NULL REFERENCES foods(id),
                quantity    FLOAT NOT NULL DEFAULT 100,
                unit        TEXT DEFAULT 'g',
                calories    FLOAT DEFAULT 0,
                protein     FLOAT DEFAULT 0,
                carbs       FLOAT DEFAULT 0,
                fat         FLOAT DEFAULT 0,
                created_at  TIMESTAMPTZ DEFAULT now()
            )
        """)
    conn.commit()


# ── Import ────────────────────────────────────────────────────────────────────

def import_batch(conn, batch: list[dict]):
    with conn.cursor() as cur:
        for item in batch:
            food_id  = item["food_id"]
            aliases  = item["aliases"]
            search_t = item["search_text"]

            cur.execute("""
                INSERT INTO foods
                    (id, food_code, canonical_name, search_text,
                     energy_kcal, protein_g, carb_g, fat_g, fiber_g, serving_unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                food_id,
                item["food_code"] or None,
                item["canonical_name"],
                search_t,
                item["energy_kcal"],
                item["protein_g"],
                item["carb_g"],
                item["fat_g"],
                item["fiber_g"],
                item["serving_unit"],
            ))

            # Retrieve actual id (might already exist via ON CONFLICT)
            cur.execute("SELECT id FROM foods WHERE food_code = %s", (item["food_code"],))
            row = cur.fetchone()
            if row:
                food_id = row[0]

            for alias in aliases:
                cur.execute("""
                    INSERT INTO food_aliases (id, food_id, alias_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (str(uuid.uuid4()), food_id, alias))

    conn.commit()


def main():
    print("=" * 60)
    print("Sarvarasa — INDB 2024.11 Import (trigram edition)")
    print("=" * 60)
    print(f"  DB  : {DB_URL_RAW[:40]}…")
    print(f"  File: {INDB_PATH}")
    print()

    # ── Schema ────────────────────────────────────────────────────────────────
    print("[1/4] Setting up schema…")
    conn = new_conn()
    setup_schema(conn)
    print("      Schema + trigram indexes ready.")

    # ── Load Excel ────────────────────────────────────────────────────────────
    print(f"[2/4] Loading {INDB_PATH.name}…")
    df = pd.read_excel(str(INDB_PATH), engine="openpyxl")
    print(f"      {len(df)} rows × {len(df.columns)} columns.")

    # ── Check already-imported ────────────────────────────────────────────────
    with conn.cursor() as cur:
        cur.execute("SELECT food_code FROM foods WHERE food_code IS NOT NULL")
        already = {r[0] for r in cur.fetchall()}
    print(f"      {len(already)} foods already in DB — skipping them.")

    # ── Build items ───────────────────────────────────────────────────────────
    print("[3/4] Processing rows…")
    items = []
    for _, row in df.iterrows():
        code = str(row.get("food_code", "")).strip()
        name = str(row.get("food_name", "")).strip()

        if not name or name.lower() == "nan":
            continue
        if code and code in already:
            continue

        canonical, extra_aliases = _extract_parenthetical_aliases(name)

        macros = {}
        for excel_col, our_col in MACRO_COLS:
            macros[our_col] = _safe(row.get(excel_col, 0))

        aliases = _build_aliases(canonical, extra_aliases)
        search_text = canonical.lower() + " " + " ".join(aliases)

        items.append(dict(
            food_id       = str(uuid.uuid4()),
            food_code     = code or None,
            canonical_name = canonical,
            search_text   = search_text,
            energy_kcal   = macros.get("energy_kcal", 0.0),
            protein_g     = macros.get("protein_g", 0.0),
            carb_g        = macros.get("carb_g", 0.0),
            fat_g         = macros.get("fat_g", 0.0),
            fiber_g       = macros.get("fiber_g", 0.0),
            serving_unit  = _infer_serving_unit(canonical),
            aliases       = aliases,
        ))

    print(f"      {len(items)} new foods to insert.")
    if not items:
        print("Nothing to do.")
        conn.close()
        return

    # ── Batch import ──────────────────────────────────────────────────────────
    print("[4/4] Inserting in batches…")
    inserted = 0

    for start in range(0, len(items), BATCH_SIZE):
        batch = items[start: start + BATCH_SIZE]
        try:
            conn.close()
        except Exception:
            pass
        conn = new_conn()
        import_batch(conn, batch)
        inserted += len(batch)
        print(f"      {inserted}/{len(items)} inserted…")

    try:
        conn.close()
    except Exception:
        pass

    print()
    print(f"Done — {inserted} foods imported.")
    total_aliases = sum(len(i["aliases"]) for i in items)
    print(f"       ~{total_aliases} aliases generated.")
    print("=" * 60)


if __name__ == "__main__":
    main()
