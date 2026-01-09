from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "cyberarena.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

if not SCHEMA_PATH.exists():
    raise FileNotFoundError(f"schema.sql not found at {SCHEMA_PATH}")

conn = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    conn.executescript(f.read())

conn.close()
print("Database initialized successfully")
