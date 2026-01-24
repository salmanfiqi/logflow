from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import json
from kafka import KafkaProducer
from indexer.db.sqlite import connect, init_db
import os

app = FastAPI()

producer: KafkaProducer | None = None

TOPIC = os.getenv("KAFKA_TOPIC", "logs")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")


@app.on_event("startup")
def startup():
    """
    Initialize Kafka producer once the app starts.
    """
    global producer
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
class LogEvent(BaseModel):
    """
    Schema (Log Event) defintion for a log event sent to ingest API

    This field validates incoming log data at system boundary. Fields here 
    represent the minumum required data for a log structure, for logs entering
    the logflow
    """
    timestamp: str
    service: str
    level: str
    message: str
    trace_id: str | None = None

class BatchLogRequest(BaseModel):
    """
    Schema (Batch Log Request) defintion for a log event sent to ingest API

    This field validates incoming log data at system boundary. Fields here
    represent the minumum required data for a log structure, for logs entering
    the logflow
    """
    logs: list[LogEvent] = Field(min_length=1, max_length=500)

@app.post("/logs")
async def ingest_log(log: LogEvent):
    """
    Accepts a single log event.

    Validates input, assigns unique event id,
    publishes to Kafka, and persists to SQLite.
    """

    event_id = str(uuid.uuid4())

    enriched_log = {
        **log.model_dump(),
        "ingest_ts": datetime.utcnow().isoformat(),
        "event_id": event_id,
    }

    try:
        producer.send(TOPIC, enriched_log)
        producer.flush(timeout=2)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Kafka publish failed: {e}")

    conn = connect()
    init_db(conn)  # safe to call repeatedly

    conn.execute(
        """
        INSERT INTO logs (
            event_id,
            ingest_ts,
            ts,
            service,
            level,
            message,
            trace_id,
            raw_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            enriched_log["event_id"],
            enriched_log["ingest_ts"],
            enriched_log["timestamp"],
            enriched_log["service"],
            enriched_log["level"],
            enriched_log["message"],
            enriched_log.get("trace_id"),
            json.dumps(enriched_log),
        ),
    )

    conn.commit()
    conn.close()

    return {"status": "accepted", "event_id": event_id}

@app.post("/logs/batch")
async def ingest_logs_batch(batch: BatchLogRequest):
    """
    Accepts a batch of log events.

    Assigns unique event IDs, publishes to Kafka,
    and persists all logs atomically to SQLite.
    """

    ingest_ts = datetime.utcnow().isoformat()
    event_ids = []
    enriched_logs = []

    for log in batch.logs:
        event_id = str(uuid.uuid4())
        event_ids.append(event_id)

        enriched_logs.append({
            **log.model_dump(),
            "ingest_ts": ingest_ts,
            "event_id": event_id,
        })

    try:
        for enriched in enriched_logs:
            producer.send(TOPIC, enriched)
        producer.flush(timeout=5)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Kafka publish failed: {e}")

    conn = connect()
    init_db(conn)

    conn.executemany(
        """
        INSERT INTO logs (
            event_id,
            ingest_ts,
            ts,
            service,
            level,
            message,
            trace_id,
            raw_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                e["event_id"],
                e["ingest_ts"],
                e["timestamp"],
                e["service"],
                e["level"],
                e["message"],
                e.get("trace_id"),
                json.dumps(e),
            )
            for e in enriched_logs
        ],
    )

    conn.commit()
    conn.close()

    return {
        "status": "accepted",
        "count": len(enriched_logs),
        "event_ids": event_ids,
    }

