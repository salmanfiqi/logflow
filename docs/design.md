# LogFlow Design Document (MVP)

## 1. Overview

LogFlow is a minimal, durable log ingestion and search system designed to explore the core building blocks of production logging pipelines. The system focuses on **correctness, durability, and queryability**, prioritizing a simple and reliable end-to-end flow over scale.

LogFlow is intentionally scoped as an MVP to validate system boundaries, data modeling, and failure behavior before introducing additional distributed components.

---

## 2. Goals

### Primary Goals
- Reliably ingest logs from multiple services
- Ensure logs are durably stored before acknowledgment
- Support basic search by time range, service, level, and text
- Provide consistent read-after-write semantics
- Run locally with minimal operational overhead

### Non-Goals
- Horizontal scalability at large volumes
- Exactly-once delivery guarantees
- Real-time streaming or alerting
- Distributed search backends

---

## 3. High-Level Architecture

### MVP Architecture
Client
↓
Ingest API (FastAPI)
↓
SQLite (WAL mode, indexed)  ← source of truth
↑
Search API (FastAPI)

---

## Components

### Ingest API
- Stateless HTTP service
- Validates and enriches incoming logs
- Persists logs durably before returning success

### Storage
- SQLite database with WAL enabled
- Indexed for efficient filtering and time-based queries

### Search API
- Read-only HTTP API
- Executes parameterized SQL queries
- Supports filtering and pagination

---

## Data Model

### Log Event

Required fields:
- `timestamp`
- `service`
- `level`
- `message`

Optional fields:
- `trace_id`

Enriched at ingestion:
- `ingest_ts`
- `event_id`

---

## Interfaces

### `POST /logs`
- Accepts a single log event
- Persists the log durably
- Returns an acknowledgment

### `POST /logs/batch`
- Accepts multiple log events
- Persists logs atomically

### `GET /search`
Query parameters:
- `service`
- `level`
- `q` (text search)
- `from` / `to` (time range)
- `limit`, `offset`

Results are returned newest first.

---

## Delivery & Failure Semantics

- Logs are acknowledged only after durable persistence
- Read-after-write consistency is guaranteed
- WAL mode ensures durability across crashes
- No in-memory state is required for correctness

---

## Technology Choices

- Python
- FastAPI
- Pydantic
- SQLite (WAL mode)
- Docker Compose

---

## MVP Completion

The MVP is complete when:
- Logs are durably stored
- Logs are immediately searchable
- Filters and pagination work as expected
- The system runs end-to-end locally