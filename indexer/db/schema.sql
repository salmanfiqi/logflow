-- Durable Log (SQL LITE)

PRAGMA journal_mode = WAL; -- switch SQL to WAL
PRAGMA foreign_keys = ON; -- key constrains

CREATE TABLE IF NOT EXISTS logs (
  event_id   TEXT PRIMARY KEY, -- assign unique id
  ingest_ts  TEXT NOT NULL, -- time stamp when log accepted

  ts         TEXT NOT NULL, -- original time stamp
  service    TEXT NOT NULL, -- logical service name
  level      TEXT NOT NULL, -- log severity
  message    TEXT NOT NULL, -- human readable log message
  trace_id   TEXT,

  raw_json   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_ingest_ts ON logs(ingest_ts); -- fast queries by ingest time
CREATE INDEX IF NOT EXISTS idx_logs_service_ts ON logs(service, ts); -- query logs for service over time
CREATE INDEX IF NOT EXISTS idx_logs_level_ts ON logs(level, ts); -- filter by time and severity