# Technical Depth — Anomaly Pipeline & Architecture

Overview
- Helios converts meter telemetry into high‑confidence, evidence‑backed alerts that feed a surgical inspection workflow. The pipeline emphasizes reliability, scale, auditability and a tight feedback loop so inspectors improve models and ROI faster than manual approaches.

Pipeline (step‑by‑step)
1. Edge collection & buffering
   - Sources: MDMS/AMI exports, direct meter telemetry, periodic CSV/FTP batches.
   - Edge gateway responsibilities: local buffering, batching, TLS credential rotation, backoff/retry and minimal pre‑aggregation to reduce writes and costs.
2. Ingestion API
   - Stateless FastAPI endpoints validate schema (Pydantic), authenticate sources, enforce idempotency keys, and enqueue normalized messages for downstream processing.
3. Preprocessing & Data Quality (DQ)
   - Normalize timestamps (tz‑aware), validate fields, deduplicate records, detect clock drift and missing windows.
   - Assign a DQ score and attach flags (late, truncated, duplicate) so downstream scoring can use confidence gating.
4. Feature extraction
   - Compute windowed aggregates (1h, 24h), deltas, seasonal features, rate changes, and enrich with meter metadata.
   - Execute in workers; cache intermediate windows for reuse across models and reporting.
5. Scoring engine
   - Lightweight inference (ONNX/TensorFlow/PyTorch runtime) combined with deterministic business rules.
   - Ensemble outputs a single confidence score; record model version and feature snapshot for provenance.
6. Evidence capture & signing
   - Attach photos or meter images when available; compute SHA‑256 hashes and sign/store hashes for non‑repudiation.
7. Alert creation & provenance
   - Persist alert records with DQ metadata, features, model version, confidence and evidence links in the canonical DB.
8. Orchestration & dispatch
   - Workflow system (Celery/Temporal/Argo) manages assignment, routing, retries, SLA checks and inspector scheduling.
9. Field inspection & resolution
   - Inspector mobile/web app shows evidence, allows one‑tap confirm/deny, captures photos/signatures and returns resolution metadata.
10. Feedback loop & retraining
   - Labeled outcomes feed training pipelines (feature store → training → validation → model registry). Regular retrain cadence and canary deploys improve precision over time.
11. Auditing, billing & reporting
   - Record audit events for every action; compute recovered amounts and generate reports for billing and DISCOM review.

Architecture (component overview)
- Edge gateways (MQTT/HTTP) → Ingestion API (FastAPI) → Message queue (Redis/Kafka) → Scoring workers (autoscaled) → Time‑series DB (Postgres/Timescale) + Object store (S3) for evidence → Workflow/orchestration → Inspector UI.
- Supporting services: Auth & secrets (Vault/KMS), Model registry, Monitoring (Prometheus/Grafana), Logging & tracing (ELK/Tempo).

Scalability & reliability design
- Decoupling via queues buffers bursts and allows independent scaling of ingestion and scoring.
- Stateless APIs, autoscaled worker pools and hypertables/partitions in TimescaleDB enable horizontal scale.
- Edge aggregation, replay windows and dead‑letter queues handle unreliable networks and late data.
- Idempotency, backpressure and circuit breakers protect downstream services under high load.

Security & compliance
- Mutual TLS for device/edge authentication; OAuth2 + RBAC for users; encryption at rest using KMS; signed evidence for non‑repudiation.
- Deploy in‑region or on‑prem to satisfy data residency and regulatory requirements.

Operational considerations
- Observability: track ingest rate, DQ fail rate, scoring latency, precision@topK, time‑to‑inspect and cost‑per‑recovery.
- SLOs and runbooks: define ingestion and scoring latency SLOs, automatic retries, and incident runbooks for production failures.
- Backup & DR: scheduled DB snapshots, multi‑region object store replication for evidence, and tested restore procedures.

Example tech stack (illustrative)
- API: FastAPI + Pydantic
- Queue: Redis Streams or Kafka
- Models: ONNX / PyTorch / TF + model registry
- DB: Postgres + TimescaleDB
- Storage: S3‑compatible object store
- Orchestration: Celery / Temporal / Argo
- Observability: Prometheus / Grafana / ELK / Tempo

Key design tradeoffs
- Real‑time vs batch: prefer near‑real‑time scoring for fast dispatch, but use batch windows where network cost dominates.
- Precision vs recall: prioritize precision at the top of the ranked list to maximize inspector ROI; expand recall after human‑in‑loop validation.

Next steps
- Produce a visual architecture diagram for slides and investor materials.
- Define the ingestion API contract and provide a minimal inspector UI prototype for pilot.
- Add pilot dashboards and instrument precision@topK, recovered revenue and inspector throughput.
