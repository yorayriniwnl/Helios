# Existing Solutions — What exists, what's missing, and what Helios solved

Short summary
- Many vendors and internal tools provide telemetry, rules or manual inspection services. What is broadly missing is a single, operational system that (1) finds high‑value theft reliably, (2) proves it with signed evidence, and (3) ties detection to a low‑cost inspection workflow that recovers revenue. Helios fills that gap.

What exists today
- MDMS / AMI dashboards: show raw reads and basic reporting; useful for billing but not optimized for targeted enforcement.
- Vendor analytics (meter OEM / MDMS add‑ons): vendor‑specific rules and alarms, often limited to device signals and lacking field evidence.
- Manual inspection services and NTL contractors: human expertise but costly, slow, and reactive — they require good triage to be efficient.
- Generic anomaly/observability platforms: detect statistical outliers but produce high false‑positive rates for enforcement use cases.
- Mobile inspection apps: capture evidence but are often disconnected from scoring models and lack signed, auditable evidence flows.

What’s missing (the gaps)
- Precision at the top: most systems flag many low‑value anomalies, forcing inspectors to chase noise.
- Evidence + auditability: photos, hashes, signatures and auditable provenance are often absent or scattered across systems.
- ROI prioritization: alerts are rarely scored by expected recovery or inspection cost, so field effort isn't optimized.
- Human‑in‑the‑loop learning: the feedback loop from inspector outcomes back into models is typically weak or manual.
- Low‑bandwidth / edge readiness: many tools assume persistent connectivity and struggle to operate in constrained networks.
- Operability & scale: limited support for production patterns (idempotency, autoscaling, partitioned time‑series, observability) in off‑the‑shelf analytics.
- Legal defensibility: missing non‑repudiable evidence storage and signed audit trails needed for enforcement and billing disputes.

What Helios solved (where we add value)
- Precision‑first detection: hybrid rules + ML tuned for precision@topK so inspectors see fewer, higher‑value cases.
- Evidence with non‑repudiation: photos and meter evidence are hashed and recorded, with signatures and audit trails for legal defensibility.
- ROI gating & dispatch: alerts are ranked by expected recovery vs inspection cost; only high‑ROI cases are dispatched automatically.
- Human‑in‑the‑loop learning: inspector confirmations feed regular retraining cycles, improving precision and reducing cost per recovery.
- Edge & DQ resilience: edge aggregators, replay buffers and data‑quality gating handle late/partial data and low connectivity environments.
- Production readiness: stateless ingestion APIs, autoscaled workers, partitioned Timescale/Postgres storage, observability and DR plans.
- Inspector‑first UX & workflows: Action Queue, one‑tap evidence capture, inspector routing and signed confirmations to close the loop quickly.

Proof points in the repo
- Demo tooling and a trigger script, sample payloads, and a DB‑level end‑to‑end test exist to demonstrate the flow and validate detection → alert → persistence.

Short competitor comparison (high level)
- Manual services: high recall in person, very low scale and high cost → Helios automates triage to make inspections surgical.
- MDMS vendor analytics: good device telemetry but limited evidence and ROI features → Helios plugs into telemetry and adds scoring + evidence + dispatch.
- Generic anomaly SaaS: broad detection, poor enforcement focus → Helios optimizes for inspector ROI and legal auditability.

Next steps for adoption
- Integrate with an MDMS export (pilot), run a 5k‑meter 3‑month pilot, measure precision@topK and recovered revenue, then refine routing and retraining cadence.
