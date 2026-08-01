# Investor Pitch — Helios

One‑liner
- Helios finds and fixes utility revenue leakage from theft and tampering with high‑precision detection and evidence‑backed inspections that pay for themselves.

Executive summary
- Problem: utilities lose significant, recurring revenue to non‑technical losses (NTL): theft, tampering and bypasses. Manual triage is slow and unfocused.
- Solution: automated time‑series anomaly detection + photo/evidence capture + a confidence‑gated inspection workflow that sends field teams only the highest‑value cases.
- Why it matters: targeted inspections recover revenue quickly, reduce field costs and restore trust with stakeholders.

Market opportunity
- TAM (global, estimate): $10B–$50B of addressable lost‑revenue reduction opportunities (range reflects regional variance in AT&C/NTL levels and utility scale).
- SAM (initial target): $1B–$5B across emerging‑market DISCOMs and high‑loss segments.
- SOM (first 3 years): $10M–$100M achievable via city/regional rollouts and enterprise contracts.
- Note: these are directional estimates — exact sizing depends on region selection, ARPU and regulatory openness.

Business model & unit economics
- Pricing: SaaS subscription + per‑inspection fee + success/recovery share (contingency), optional managed services for large utilities.
- Example pilot economics (5k meters):
  - Alerts/month: 100; precision@top → 20% → 20 confirmed recoveries
  - Avg recovered value per success: $300 → gross recovered $6,000/month
  - Inspection cost: 20 * $30 = $600; platform & ops $2,000 → total $2,600
  - Net recovery: $3,400/month; platform revenue (20% success fee): $1,200/month
  - Conclusion: modest pilots can show positive unit economics and payback in months depending on local ARPU and inspector costs.

ROI for customers & investors
- Measurable KPIs: precision@topK, recovered revenue, time‑to‑inspect, cost‑per‑recovery, and ROI per inspection.
- Fast feedback loop: inspector labels and recovered revenue feed weekly model retraining, improving precision and lowering cost per recovery.
- Scaling multiplies returns because marginal cost per additional meter is low after models are tuned regionally.

Scalability & tech path
- Architecture: edge aggregators → stateless ingestion APIs → message queue → idempotent scoring workers → object store (evidence) + time‑series DB (Postgres/Timescale).
- Scaling levers: autoscaled worker pools, hypertables/partitioning, read replicas, edge aggregation to reduce write volume, and caching for hot analytical queries.
- Operational playbook: pilot → regional scaling with local partners → multi‑region deployments for national rollouts.

Go‑to‑market & partnerships
- Priority partners: MDMS/AMI vendors, telecom/IoT providers for constrained networks, local inspection contractors and DISCOM/regulator champions.
- Pilot approach: 1–3 city pilots (5k meters each) with tight KPI measurement and full inspector integration; convert to enterprise contracts on validated ROI.

Funding ask & use of funds (suggested)
- Seed range: $500k – $1.5M to run multiple pilots, productize inspector UX, scale engineering and sales, and cover operations for 12–18 months.
- Use: ~40% product & ML, 30% pilot ops & partnerships, 20% GTM & regulatory, 10% contingency.

Next steps & CTA
- Run a 3‑month pilot, measure precision@topK and recovered revenue, then scale regionally after demonstrating >2x ROI on pilot economics.
- We ask investors to fund the pilot program and channel partnerships to accelerate regional expansion.

Notes
- All numeric examples are illustrative — local ARPU, inspection costs and regulatory constraints will determine final business cases.
