import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(os.getenv("LOGFLOW_DB_PATH", "logflow.db")) # read logflow, lets us store db

def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
        Defines a helpter to open db
        Defaults to db path
    """
    conn = sqlite3.connect(db_path) # opens the sqlite file
    conn.row_factory = sqlite3.Row # makes query results like a dict
    conn.execute("PRAGMA journal_mode=WAL;") # enable WAL
    conn.execute("PRAGMA synchronous=NORMAL;") # set to normal
    conn.execute("PRAGMA foreign_keys=ON;") # enforce key
    return conn # return full config db

def init_db(conn: sqlite3.Connection) -> None:
    """
        Initliaze db schema
    """
    schema_path = Path(__file__).with_name("schema.sql") # find schema.sql direc
    schema_sql = schema_path.read_text(encoding="utf-8") # read the sql schema
    conn.executescript(schema_sql) # execute sql statements
    conn.commit() # schema change to disk