*** Begin Q&A ***
# Judge Q&A — Scalability, ML Validity, Real-World Usage, Deployment, Cost

Purpose: 20 sharp technical questions a judge will ask, with short confident answers.

1. Q: What's the main ingestion bottleneck at high throughput?
   A: Synchronous DB commits and per-event CPU (detection); fix with a durable broker, batched writes, and horizontally scaled stateless ingesters.

2. Q: How to handle 100k events/sec reliably?
   A: Partition by key into a high-throughput broker, bulk-insert into a partitioned TSDB/columnar store, autoscale consumers, and employ backpressure/downsampling.

3. Q: How to scale anomaly detection horizontally?
   A: Make detectors stateless, use stream partitioning, deploy model servers with GPU/CPU pools, and route keys to consistent consumer groups.

4. Q: How to guarantee ordered, idempotent ingestion?
   A: Use sequence numbers or idempotency keys per device, persistent dedupe store (or upserts), and write-ordered partitions in the broker.

5. Q: How to handle late or duplicate readings?
   A: Ingestion accepts event-time; use watermarking, windowed aggregation, and dedupe by (device, seq, ts) or hash key with TTL.

6. Q: How to scale real-time WebSocket fanout?
   A: Offload fanout to pub/sub (Redis/Kafka), run clustered socket gateways, use incremental diffs, and shard subscriptions by topic.

7. Q: How do you separate OLTP and analytics at scale?
   A: Write to OLTP, stream-capture to change-log, ETL into OLAP (ClickHouse/Timescale), maintain materialized views for dashboard queries.

8. Q: Which metrics prove ML validity in production?
   A: Precision@k, recall, false positive rate, AUC/PR over time, calibration error, and feature-drift statistics per window.

9. Q: How to avoid ML overfitting and operational false alarms?
   A: Temporal cross-validation, holdout by time, L2/regularization, class reweighting, and threshold tuning on operational precision targets.

10. Q: How to provide actionable explanations for alerts?
    A: Return top‑k feature attributions, rule provenance, compact templates, and patient-level snapshots (feature values + recent history).

11. Q: How to train with scarce labels?
    A: Apply weak supervision (rules, heuristics), synthetic anomaly injection, semi-supervised models (autoencoders), and active labeling pipelines.

12. Q: How to detect and react to concept drift?
    A: Monitor feature distribution (PSI/KL), monitor model metrics; trigger retrain pipelines and canary promotions when thresholds breach.

13. Q: How to reduce inference cost without losing accuracy?
    A: Use lightweight rule filters inline, batch ML inference, quantize/compile models, and route only uncertain cases to heavy models.

14. Q: What's your zero-downtime deployment pattern?
    A: Canary or blue/green deploys, feature flags, backward-compatible DB changes, and gradual traffic shift with health checks.

15. Q: How are secrets and config managed securely?
    A: Central secrets manager (Vault/KMS), runtime injection, RBAC and audit logs, and automated rotation with no hard-coded secrets.

16. Q: How to maintain availability with intermittent field connectivity?
    A: Client durable queue, idempotent ingest APIs, sequence reconciliation on reconnect, and eventual-consistency tolerant downstream processing.

17. Q: Multi-tenant isolation strategy?
    A: Per-tenant namespaces or RLS, quotas and throttles, per-tenant telemetry/billing tags, and optional per-tenant DBs for strict isolation.

18. Q: How to perform DB schema changes safely?
    A: Additive migrations, create indexes concurrently, dual-read/dual-write transition, and migrate data in small, validated batches.

19. Q: How to control storage and retention costs?
    A: Hot/cold retention policy, downsample historical data, compress columnar storage, and offload cold data to object storage with lifecycle rules.

20. Q: How do you forecast and cap cloud inference/storage cost?
    A: Model cost-per-inference benchmarks, enforce autoscaling limits, use spot instances for batch inference, and implement per-tenant quotas and alerts.

*** End Q&A ***


---
File: `docs/judge_questions_and_answers.md`
