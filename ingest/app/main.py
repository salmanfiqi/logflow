from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

# Create FAST API Instance
app = FastAPI()

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

@app.post("/logs")
async def ingest_log(log: LogEvent):
    """
    Accepts a single log event

    Validates input, assigns unique event id, and returns immidiatley
    """
    event_id = str(uuid.uuid4())
    enriched_log = {
        **log.model_dump(),
        "ingest_ts": datetime.utcnow().isoformat(),
        "event_id": event_id,
    }
    return {"status": "accepted", "event_id": event_id}