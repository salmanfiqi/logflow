import os
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

#override via env var, otherwise always write to repo-root logflow.db
DEFAULT_DB_PATH = Path(
    os.getenv("LOGFLOW_DB_PATH", str(PROJECT_ROOT / "logflow.db"))
)

def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Helper to open a SQLite connection.

    - Ensures WAL mode for concurrency
    - Ensures consistent DB location
    """
    # check_same_thread=False
    conn = sqlite3.connect(db_path, check_same_thread=False)

    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row

    # Performance + safety pragmas
    conn.execute("PRAGMA journal_mode=WAL;")        # enable WAL
    conn.execute("PRAGMA synchronous=NORMAL;")      # balanced durability
    conn.execute("PRAGMA foreign_keys=ON;")         # enforce FK constraints
    conn.execute("PRAGMA busy_timeout=3000;")       # wait before SQLITE_BUSY

    return conn

def init_db(conn: sqlite3.Connection) -> None:
    """
    Initialize DB schema if it doesn't exist.

    Safe to call multiple times.
    """
    # Load schema.sql next to this file
    schema_path = Path(__file__).with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")

    # Execute schema and commit
    conn.executescript(schema_sql)
    conn.commit()