# LogFlow

LogFlow is a distributed, fault tolerant log ingestion and search system designed to handle high-throughput logs from microservices in a scalable and reliable way.

## Motivation
Modern distributed systems generate massive volumes of logs across services, machines, and regions. LogFlow explores how production grade logging pipelines ingest, buffer, process, and search logs while remaining resilient to traffic spikes and component failures.

## High-Level Architecture
Log producers send structured logs to a stateless ingestion service. Logs are buffered through a message queue, processed asynchronously by background workers, and indexed into a search-optimized storage layer. A query API enables fast filtering and time-based searches.

## Core Components
- **Ingest API** – Accepts logs over HTTP and appends them to the queue
- **Message Queue** – Buffers logs and decouples ingestion from processing
- **Indexer Workers** – Normalize and batch logs for efficient indexing
- **Search Storage** – Stores indexed logs optimized for query performance
- **Query API** – Exposes search and filtering capabilities

## Design Goals
- Horizontal scalability
- At-least-once log delivery
- Backpressure handling
- High write throughput
- Sub-second search latency
- Failure resilience

## Tech Stack 
- Language: Python 
- Queue: Redis Streams potentially Kafka
- Storage: OpenSearch / Elasticsearch
- Containerization: Docker & Docker Compose

## Learning Objectives
This project focuses on building intuition around:
- Distributed systems design
- Queue-based architectures
- Asynchronous processing
- Indexing and search tradeoffs
- Reliability and failure handling
