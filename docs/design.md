# LogFlow Design Document

## 1. Overview
LogFlow is a distributed, fault-tolerant log ingestion and search system designed to explore scalable logging pipelines used in production systems. The system decouples log ingestion from storage using a queue to handle traffic spikes and failures gracefully.

## 2. Goals

### Goals
- Reliably ingest logs from multiple services
- Decouple ingestion from indexing using a durable queue
- Support basic search by time range, service, level, and text
- Handle failures without losing logs
- Run locally via Docker Compose

## 3. High-Level Architecture

### Components
- **Ingest API:** Stateless HTTP service that validates and enriches logs before appending them to the queue.
- **Queue:** Durable buffer that decouples ingestion from processing and supports replay on failure.
- **Indexer Workers:** Consume logs from the queue, batch them, and bulk index into storage.
- **Search Storage:** Index-optimized store supporting time-based and full-text search.
- **Query API:** Read-only API for querying logs with filters and pagination.

## 4. Data Model

### Log Event Schema

Required fields:
- `timestamp` (ISO 8601)
- `service` (string)
- `level` (DEBUG | INFO | WARN | ERROR)
- `message` (string)

Optional fields:
- `trace_id`
- `request_id`
- `host`
- `env`

Enriched by ingestion:
- `ingest_ts`
- `event_id` (optional, used for idempotency)

## 5. Interfaces

### Ingest API
- `POST /logs`
  - Accepts a single JSON log event
  - Returns success after appending to the queue

### Query API
- `GET /search`
  - Query parameters: `service`, `level`, `q`, `from`, `to`, `limit`

## 6. Delivery Semantics

LogFlow provides **at-least-once delivery**.
- Logs may be processed more than once
- Log loss is minimized
- Indexer workers acknowledge queue messages only after successful indexing

Duplicate logs are acceptable in v1. Optional idempotency can be achieved using `event_id` as the document identifier.

## 7. Failure Handling and Backpressure

- If an indexer worker crashes, unacknowledged messages remain in the queue and are replayed.
- If search storage is slow or unavailable, workers retry with backoff.
- Queue backlog serves as the primary backpressure signal.
- Ingest API remains responsive as long as the queue can accept messages.

## 8. Scaling Model

- Ingest API scales horizontally due to statelessness.
- Indexer workers scale via consumer groups.
- The queue absorbs traffic spikes.
- Search storage scales independently of ingestion.

## 9. Technology Choices

- **Language:** Python
- **Queue:** Redis Streams
- **Search Storage:** OpenSearch / Elasticsearch

Redis Streams was chosen for development speed and reliable queue semantics in v1. Kafka is a potential future replacement.

## 10. MVP Completion Criteria

The MVP is considered complete when:
- Logs sent to the Ingest API appear in search results
- End-to-end flow works under Docker Compose
- Logs can be queried by time range, service, and text
- Worker failures do not result in log loss