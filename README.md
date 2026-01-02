# LogFlow

LogFlow is a distributed, fault-tolerant log ingestion and search system built to explore scalable, production-style logging pipelines.

## Overview
LogFlow collects structured logs from microservices, buffers them through a message queue, processes them asynchronously, and indexes them for fast search and filtering. The system is designed to remain resilient under traffic spikes and component failures.

## Architecture
Producers → Ingest API → Queue → Indexer Workers → Search Storage → Query API

## Key Properties
- Stateless ingestion with asynchronous processing
- Queue-based decoupling and backpressure handling
- At-least-once delivery semantics
- Horizontally scalable components
- Failure-tolerant by design

## Tech Stack
- Python
- Redis Streams (Kafka as potential extension)
- OpenSearch / Elasticsearch
- Docker & Docker Compose

## Status
In active development. See `docs/design.md` for detailed system design and tradeoffs.