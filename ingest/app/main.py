from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
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

class BatchLogRequest(BaseModel):
    """
    Schema (Batch Log Request) defintion for a log event sent to ingest API

    This field validates incoming log data at system boundary. Fields here
    represent the minumum required data for a log structure, for logs entering
    the logflow
    """
    logs: list[LogEvent] = Field(min_length=1, max_length=500)

# Registers function as the handler for HTTPS POST /logs
@app.post("/logs")

async def ingest_log(log: LogEvent):
    """
    Accepts a single log event

    Validates input, assigns unique event id, and returns immidiatley
    """

    # Generate unique id for event; convert to string
    event_id = str(uuid.uuid4())

    # Create new dic that stores meta data
    enriched_log = {
        # Returns a dictionary
        **log.model_dump(),

        "ingest_ts": datetime.utcnow().isoformat(),
        "event_id": event_id,
    }

    return {"status": "accepted", "event_id": event_id}