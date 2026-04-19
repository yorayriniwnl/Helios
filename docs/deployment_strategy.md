# Deployment Strategy — Pilot → Smart‑meter Integration → DISCOM Scale

Goal
- Prove Helios can detect theft and recover revenue with a fast, low‑risk pilot in one city, then scale to a full DISCOM rollout with measurable ROI and operational processes.

1) Pilot in one city (recommended scope)
- City profile: medium city (0.5–1M population) with clear AT&C hotspots and a cooperative DISCOM operations team.
- Pilot scope: 5,000 meters across 3–10 feeders (covers diverse neighborhoods and feeder types). Focus on high‑loss feeders to maximize detection signal.
- Duration: 4–6 months end‑to‑end (prep → deployment → validation).
- Objectives:
  - Prove real‑time detection and localization at feeder/meter granularity.
  - Validate explainability (alert rationales + evidence) with field inspections.
  - Measure field conversion (alerts → validated recovery) and baseline AT&C change.
- Deliverables:
  - Deployed ingest pipeline and analytics for pilot meters.
  - Operational triage dashboard and mobile inspection flow.
  - Pilot report: pre/post AT&C, recovered INR, cost‑per‑inspection, recommended scale plan.

2) Smart‑meter integration (pilot → production)
- Integration tasks:
  - Vendor selection & compatibility checks (meter protocols, MDMS mapping).
  - Secure data ingestion: translation layer (protocol adapters), message schema, timestamp sync, and replay buffering.
  - MDMS / billing integration: map meter IDs, meter status, and invoice reconciliation hooks.
  - Edge/comms handling: SIM/LPWAN provisioning, local buffering for intermittent connectivity, and OTA/firmware readiness where applicable.
  - Security & privacy: TLS/Mutual auth, key management, and role‑based access for inspection evidence.
- Testing: lab acceptance (2–4 weeks), pilot field acceptance (4–8 weeks) with synthetic and live test vectors.

3) Scale to DISCOM (practical rollout plan)
- Phased rollout: tranche approach (e.g., 100k meters per tranche) to reduce operational risk and allow continuous learning.
- Organizational readiness: establish a Small Ops Center (pilot) then scale field teams, QA, and a central monitoring & audit team.
- Procurement & finance: bulk RFP for meters + installation suppliers; negotiate SIM plans and warranty SLAs.
- Operationalize: training, inspector app roll‑out, standard operating procedures, and enforcement playbook.
- Governance: set KPI cadence (weekly alerts, monthly AT&C), go/no‑go gates for each tranche.

Cost estimate (example pilot assumptions & sensitivity)
- Assumptions (base case): 5,000 pilot meters; meter HW INR 4,000 each; install INR 1,000 each; connectivity (12 months) INR 300/meter; SI & integration INR 20 Lakh; cloud & SW INR 10 Lakh; field ops & training INR 8 Lakh; contingency 15%.

Pilot cost (5,000 meters, base case)
| Item | Unit cost (INR) | Units | Total (INR) |
|---|---:|---:|---:|
| Smart meters (HW) | 4,000 | 5,000 | 20,000,000 |
| Installation & commissioning | 1,000 | 5,000 | 5,000,000 |
| Connectivity (12 months) | 300 | 5,000 | 1,500,000 |
| System integration & MDMS work | (flat) | — | 2,000,000 |
| Cloud / SW / analytics (12 months) | (flat) | — | 1,000,000 |
| Field ops, inspections & training | (flat) | — | 800,000 |
| Subtotal | | | 30,300,000 |
| Contingency (15%) | | | 4,545,000 |
| Total (pilot) | | | 34,845,000 (~INR 3.48 Cr) |

- Approx USD equivalent (exchange ≈ INR 82 = 1 USD): pilot ≈ $425k (rounded) — present in INR for procurement accuracy.
- Sensitivity: per‑meter HW ranges INR 3,000–6,000. If hardware is INR 6,000, pilot total rises to ≈ INR 4.3–4.6 Cr.

Scale estimate (ballpark)
- Marginal per‑meter cost at scale (bulk procurement): ~INR 4,000–5,000 (HW, install, connectivity).
- Example: per 100k meters → 100,000 × INR 4,500 ≈ INR 450,000,000 (~INR 45 Cr). Per 1M meters → ≈ INR 4.5B (~INR 450 Cr).
- Note: major line items at scale are procurement, installation labor, and project management; cloud/analytics scale sublinearly.

Timeline (realistic)
- Phase 0 — Prep & contracts: 4–8 weeks (stakeholder sign‑off, baseline data, RFP/SOW).
- Phase 1 — Pilot deploy: 8–12 weeks (procure, install, integrate).
- Phase 2 — Validation & process codification: 8–12 weeks (field verification, KPI measurement, playbook).
- Phase 3 — Tranche rollouts: 6–12 months per 100k tranche (parallelize where resources permit).
- Full DISCOM (0.5–2M meters): 12–36 months depending on procurement cycle and workforce capacity.

Gates & KPIs
- Go/no‑go gate after pilot: pre/post AT&C improvement on targeted feeders, ≥X% validated conversion (custom target) and positive short‑term ROI (recovered INR > pilot incremental cost over defined window).
- Operational KPIs: alerts/day, conversion rate, avg INR recovered per inspection, time‑to‑close.

Risks & mitigations
- Procurement delays: mitigate with existing supplier short‑lists and phased purchase orders.
- Meter heterogeneity: run adapter/translation layer and focus pilot where data quality is sufficient.
- Field resistance & enforcement friction: embed local DISCOM champions, provide clear inspector SOPs and evidence bundles.

Next steps (practical immediate actions)
1. Identify candidate city and DISCOM partner; get data access and a signed MoU (2–4 weeks).
2. Run procurement SOW for 5,000 meters and shortlist 2 vendors (4–6 weeks parallel).
3. Execute pilot procurement, lab acceptance, and deploy (8–12 weeks).
4. Run 8–12 week validation and finalize scale plan.

Contact & financing notes
- Use a pilot‑first financing model: vendor/dev partner funds part of pilot in exchange for performance milestone payments or pilot co‑funding by DISCOM/grant agencies.

This plan balances speed (pilot within ~3 months of procurement approval) with realism around procurement, field ops, and DISCOM governance — designed to convert detection into verified, auditable revenue recovery and a repeatable scale model.
