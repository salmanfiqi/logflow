# search/app/main.py

from fastapi import FastAPI, Query
from typing import Optional, List
from pydantic import BaseModel

from indexer.db.sqlite import connect, init_db

app = FastAPI(title="LogFlow Search API")


class LogRow(BaseModel):
    event_id: str
    ingest_ts: str
    ts: str
    service: str
    level: str
    message: str
    trace_id: Optional[str] = None


class SearchResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: List[LogRow]


@app.get("/search", response_model=SearchResponse)
def search_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    q: Optional[str] = None,
    from_ts: Optional[str] = Query(None, alias="from"),
    to_ts: Optional[str] = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    MVP search over SQLite.

    Supports:
    - filtering by service + level
    - substring search on message
    - time range on ingest_ts
    - pagination
    """

    conn = connect()
    init_db(conn)  # safe no-op if already initialized

    where = []
    params = []

    if service:
        where.append("service = ?")
        params.append(service)

    if level:
        where.append("level = ?")
        params.append(level)

    if from_ts:
        where.append("ingest_ts >= ?")
        params.append(from_ts)

    if to_ts:
        where.append("ingest_ts <= ?")
        params.append(to_ts)

    if q:
        where.append("message LIKE ?")
        params.append(f"%{q}%")

    where_sql = " WHERE " + " AND ".join(where) if where else ""

    # total count
    total = conn.execute(
        f"SELECT COUNT(*) FROM logs{where_sql}",
        params,
    ).fetchone()[0]

    # page results
    rows = conn.execute(
        f"""
        SELECT event_id, ingest_ts, ts, service, level, message, trace_id
        FROM logs
        {where_sql}
        ORDER BY ingest_ts DESC
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    ).fetchall()

    conn.close()

    return SearchResponse(
        total=total,
        limit=limit,
        offset=offset,
        results=[LogRow(**dict(r)) for r in rows],
    )