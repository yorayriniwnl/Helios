# Tech Stack Justification — Practical choices for Helios

Purpose
- Short, practical reasons for the primary technology choices used in Helios and why they reduce risk and speed deployment.

Why `FastAPI`
- Async-first web framework: native async support fits high-throughput ingestion (MQTT/webhooks/streams) without blocking worker threads.
- Development velocity: Python + `pydantic` gives fast schema validation, strong typing, and quick iteration for new telemetry sources and APIs.
- Production-ready and lightweight: small memory footprint, easy to containerize, and simple to run with `uvicorn`/`gunicorn` behind a load balancer.
- Built-in OpenAPI & testability: auto-generated API docs speed integration with DISCOM systems and simplify automated testing with `TestClient`.
- ML ecosystem fit: Python services integrate directly with model training and inference code, avoiding cross-language serialization friction.

Why `PostgreSQL`
- Source of truth & ACID guarantees: billing, recovered revenue, and inspection records require transactional integrity and strong consistency.
- Relational queries & joins: meter→feeder→zone relationships and rollups are efficient and simple in SQL compared to complex joins in many NoSQL stores.
- Time‑series scaling options: use partitioning or TimescaleDB for meter time-series, with BRIN/GIN indexes to keep query costs low.
- Hybrid model support: `JSONB` for flexible telemetry metadata plus relational schemas for financial and operational data.
- Ops maturity: backups, replicas, PITR, and monitoring are well understood and supported by standard tools — lowers operational risk for DISCOM pilots.

Why an ML approach (practical, not academic)
- Theft patterns are varied and evolving: rule-only systems generate noise and miss stealthy, localized fraud; ML adapts to patterns and reduces false positives.
- Hybrid & incremental: start with conservative rules and lightweight supervised models (or ensemble) so operators see immediate, reliable gains while models learn.
- Forecasting + anomaly detection: per‑meter and feeder forecasts create context for deviations (helps prioritize true theft vs load changes).
- Explainability & operator trust: models are deployed with simple explainers (feature scores, event timelines, example fingerprints) so inspectors have defensible evidence.
- Low operational cost: inference is cheap — models can run in the cloud, in edge aggregators, or as small microservices; batching and caching cut costs further.
- Human-in-the-loop: operator labels and inspection outcomes feed back into models, improving precision and reducing field costs over time.

Practical trade-offs & alternatives
- FastAPI vs heavier frameworks: alternatives (Django) add features but more overhead; FastAPI hits the right balance of speed, developer ergonomics, and observability for APIs and streaming endpoints.
- PostgreSQL vs NoSQL/time-series-only stores: NoSQL can store raw telemetry, but PostgreSQL (±Timescale) keeps a single authoritative place for billing, reconciliation and joins — simpler for DISCOM workflows.
- ML vs rule-only: rules are inexpensive to start but scale poorly (maintenance, false positives). A pragmatic hybrid approach minimizes operational disruption while improving detection.

Operational notes
- Deploy FastAPI as containerized services (Kubernetes or managed containers) with autoscaling; use connection pooling for PostgreSQL and read replicas for analytics.
- Use TimescaleDB or partitioning for large meter time‑series, keep Postgres as the canonical DB for billing and audit trails.
- Serve models via a small, versioned model service or embed lightweight models in the API; store model metadata and performance in a registry.
- Observability: metrics (Prometheus), structured logs, and tracing are mandatory to validate detection speed and support SLA guarantees.

Next steps
- Align data contracts (timestamps, meter IDs) with pilot DISCOM and create a short checklist for operations (MDMS exports, data quality gates, security requirements).
