# LogFlow

LogFlow is a distributed, fault-tolerant log ingestion and search system built to explore scalable, production-style logging pipelines.

The project focuses on correctness, durability, and system design fundamentals.

---

## Overview

LogFlow collects structured logs from services, validates and enriches them at ingestion time, buffers them through a durable queue, persists them reliably, and exposes a read-optimized search API.

The system is designed to:
- Remain responsive under traffic spikes
- Decouple ingestion from storage and querying
- Tolerate component failures without losing logs
- Mirror real-world logging system architecture at a smaller scale

---

## High-Level Architecture

Log Producers
|
v
Ingest API (FastAPI)
|
v
Kafka
|
v
Durable Storage (SQLite, WAL)
|
v
Search API (FastAPI)

---

## Core Components

### Ingest API
- HTTP service built with FastAPI
- Validates incoming log schema
- Enriches logs with metadata:
  - `event_id`
  - `ingest_ts`
- Publishes logs to Kafka
- Persists logs to durable storage
- Returns immediately after successful ingestion

### Queue (Kafka)
- Acts as a durable buffer between ingestion and downstream processing
- Decouples write and read paths
- Absorbs traffic spikes
- Enables replay and recovery on failure

### Storage Layer
- SQLite database with WAL mode enabled
- Optimized for durability and concurrent reads
- Indexed by:
  - ingest timestamp
  - service
  - log level
- Serves as the system of record for logs

### Search API
- Read-only FastAPI service
- Queries logs directly from durable storage
- Supports:
  - Filtering by service and log level
  - Time-range queries
  - Substring text search
  - Pagination with limit and offset
- Returns results ordered by newest logs first

---

## Data Model

Each log event contains:

**Required fields**
- `timestamp` (ISO 8601)
- `service`
- `level`
- `message`

**Optional fields**
- `trace_id`

**Enriched fields**
- `event_id`
- `ingest_ts`

---

## Delivery Semantics

LogFlow provides **at-least-once delivery** semantics.

- Logs may be processed more than once
- Log loss is minimized
- Duplicate entries are acceptable in the MVP
- Idempotency can be added using `event_id` as a unique identifier

---

## Failure Handling

- If Kafka is temporarily unavailable, ingestion fails fast
- If downstream consumers fail, logs remain in the queue
- Durable storage ensures logs are not lost after ingestion
- WAL mode allows concurrent reads while writes continue

---

## Scalability Model

- Ingest API scales horizontally due to statelessness
- Kafka absorbs load spikes and smooths traffic
- Search API scales independently from ingestion
- Storage can be replaced with a distributed search system in future iterations

---

## Tech Stack

- **Language:** Python
- **APIs:** FastAPI
- **Queue:** Kafka
- **Storage:** SQLite (WAL mode)
- **Infrastructure:** Docker & Docker Compose

---

## Status

MVP complete.

LogFlow successfully supports:
- End-to-end ingestion
- Durable persistence
- Search by service, time, and text
- Local execution via Docker Compose