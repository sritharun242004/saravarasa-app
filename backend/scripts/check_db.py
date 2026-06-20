import psycopg2, re, os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://","").replace("postgresql://","")
m = re.match(r"([^:]+):([^@]+)@([^/]+)/([^?]+)", url)
user, pwd, host, db = m.groups()
dsn = f"host={host} dbname={db} user={user} password={pwd} sslmode=require"

conn = psycopg2.connect(dsn, connect_timeout=15)
cur = conn.cursor()

tables = ["foods","food_nutrients","food_aliases","categories","regions","nutrients","ingredients"]
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t}: {cur.fetchone()[0]}")
    except Exception as e:
        print(f"  {t}: ERROR - {e}")
        conn.rollback()

print()
cur.execute("SELECT name FROM foods LIMIT 5")
for r in cur.fetchall():
    print(f"  Sample food: {r[0]}")

conn.close()
