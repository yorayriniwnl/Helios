# Deployment Readiness — What’s needed for real deployment (practical)

Purpose
- A concise, practical checklist that answers: what is required to run Helios in production, and what the absolute minimal infrastructure looks like for a low‑risk pilot.

1) Production essentials (short, practical list)
- Reliable ingestion: robust, idempotent ingestion APIs (MQTT/webhook/S3 import) with timestamp normalization, dedupe and replay buffering.
- Durable storage: PostgreSQL (primary store for billing, audit, inspections) with WAL archiving, PITR and read replicas; object storage (S3-compatible) for raw meter dumps, photos, and evidence.
- Time‑series support: TimescaleDB (or PostgreSQL partitioning) for efficient range queries and retention policies.
- Model serving & orchestration: containerized model microservice(s) or a lightweight model server with versioning; productionized CI for model promotions.
- Queueing & workers: Redis or managed queue (SQS/Kafka/Rabbit) for background jobs (scoring, retries, ingestion backpressure, mobile sync).
- API services: containerized FastAPI apps behind an LB/ingress with autoscaling (k8s or managed container platform). Use nginx/Traefik for TLS termination if not handled by cloud LB.
- Secrets & config: secrets manager (AWS Secrets Manager / Vault) and config stored in environment or config service — never plaintext in repo.
- Security & identity: TLS mutual auth for meter/edge ingestion where possible, RBAC for UI and APIs, encrypt at rest and in transit, and audit logging for all enforcement events.
- Observability & SRE: Prometheus metrics, Grafana dashboards, structured logs (ELK or hosted), tracing for alert pipelines, and alerting (pager/on‑call) for SLO breaches.
- Backup & DR: automated DB backups, periodic restore drills, and an object‑storage lifecycle for raw evidence retention.
- CI/CD & IaC: GitHub Actions (or equivalent) for CI; Terraform (or cloud native IaC) for repeatable infra. Deploy staging = prod‑parity for safety.

2) Minimal infra for a low‑risk pilot (practical, managed components)
Goal: run a 5k‑meter pilot with minimal ops overhead.

- Recommended minimal stack (managed services to reduce ops):
  - Managed Postgres (RDS / Cloud SQL) with daily backups and a small read replica.
  - A small container host: Cloud Run / Fargate / a single k8s node pool (3 small nodes) to run API + workers.
  - Managed object storage (S3) for evidence and raw exports.
  - Managed Redis (Elasticache) or a small instance for caching/queueing.
  - Basic monitoring: CloudWatch / Prometheus (hosted) + simple Grafana dashboards.
  - CDN / LB with TLS (managed) for API endpoints.

- Minimal on‑prem alternative (if cloud not allowed):
  - One small VM for API+worker (t3.medium or equivalent) + one managed Postgres VM; object storage via on‑prem storage with SFTP; local Redis.
  - Note: this increases ops burden — prefer managed services for pilot.

- Cost ballpark (pilot infra only):
  - Managed Postgres small: ~$50–200/month
  - Small container compute (Fargate/Cloud Run): ~$50–200/month
  - Redis managed small: ~$20–100/month
  - S3/storage + network: <$50–150/month depending on ingestion.
  - Monitoring & logs: $0–200/month depending on retention and provider.
  - Total pilot infra estimate: roughly $170–900/month (cloud credits or grant can reduce this).

3) Operational and non‑tech requirements (practical)
- Data contracts: clear MDMS/AMI export spec (meter_id, timestamp, kWh, timezone) and an agreed ingestion cadence. Run a Data Quality Report before enforcement.
- Field playbook: inspector SOPs, evidence checklist, mobile app workflows and training, and SLAs for turnaround.
- Legal & compliance: signed MoU with DISCOM on inspection & enforcement protocols, evidence admissibility, and data retention policy.
- People: a small on‑call engineering rota, a data scientist for model tuning, and a field ops lead during piloting.

4) Model & data‑ops (practical)
- Training & retraining: schedule weekly retraining loops during the pilot with human‑in‑the‑loop labels from inspections.
- Model registry & versioning: tag model versions, keep performance metrics, and provide easy rollback.
- Feature stores / caching: keep a short‑term feature cache for low‑latency scoring (Redis) and a historical store for offline retraining (Timescale/S3).

5) Security, audit, and evidence chain (must‑have)
- Chain of custody: every inspection/photo has signed metadata (inspector id, timestamp, GPS, photo hash) persisted in the audit DB and S3.
- Authentication: integrate SSO or secure user management for inspectors; use RBAC to control who can trigger enforcement actions.
- Encryption & keys: keys in a secrets manager; encrypt evidence at rest; rotate keys on schedule.

6) Observability & SLOs (practical targets)
- Ingestion latency SLO: 95% of reads processed within 30s (pilot can be relaxed to 95% within 5 minutes).
- Alert precision target (pilot): high‑confidence tier ≥ 85% precision within 4 weeks as models tune.
- Uptime: API 99.9% for critical endpoints during pilot demo windows.

7) Runbooks & deployment practices (practical)
- Canary releases and feature flags for model promotions and UI changes.
- Automated health checks and rollback triggers on deploy failures.
- Routine DR drill: quarterly restore from backup to staging and validate core flows (ingest → detect → evidence capture).

8) Quick checklist to go from pilot → production
1. Complete pilot with validated pre/post KPIs and inspect evidence for 30–90 days. 2. Harden infra (replicas, backups, DR). 3. Formalize SOPs, legal approvals, and training program. 4. Move from single‑region to multi‑region redundancy if DISCOM requires higher availability. 5. Prepare procurement & capex plan for meter install scaling.

9) Practical next steps I can do for you
- Provide Terraform skeleton for the minimal pilot infra.
- Add a sample k8s manifest + deployment pipeline for the FastAPI service.
- Produce a small cost model tailored to your cloud provider and target meter counts.

Files added: none (this is guidance). If you want, I will add `docs/deployment_readiness.md` to the repo now.

Confident closing
- This is a pragmatic, low‑risk path: start with managed services for the pilot, validate the operational playbook and DQ gates, then scale with repeatable IaC and canaryed rollouts. I can produce deployment templates and a one‑page SLA to hand to DISCOMs next.
