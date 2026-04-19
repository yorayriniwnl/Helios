# Future Roadmap — Timeline‑Based Vision for Helios

Purpose
- Present a realistic, time‑boxed path from a validated pilot to a DISCOM‑scale smart‑grid platform that combines smart‑meter integration, AI forecasting, and a field‑first mobile app.

Short term (0–6 months) — Pilot consolidation & MVP
- Objectives:
  - Complete pilot validation (5k meters): finalize ingest pipelines, streaming anomaly detection, and evidence capture.
  - Deliver an inspector Mobile MVP: offline photo capture, geo‑tagging, signature, case creation and basic worklist sync.
  - AI forecasting POC: baseline per‑meter and feeder consumption forecasts used to tighten anomaly thresholds (daily/hourly models).
  - Smart‑grid integration (baseline): MDMS mapping, meter ID reconciliation, and an ingestion adapter for AMI/MDMS exports or MQTT streams.
- Deliverables:
  - `Mobile MVP` (iOS/Android wrapper or PWA) with photo + geotag + offline queue.
  - `Forecasting` models (per‑meter seasonal+diurnal baseline) integrated into the detection pipeline.
  - `MDMS adapter` and ingestion tests against pilot data.
- Success metrics:
  - Detection speed: median alert <24 hours from event.
  - Field conversion: ≥30% of alerts validated as true theft or actionable within pilot window.
  - Pilot report: pre/post AT&C, recovered kWh/INR, cost‑per‑inspection.

Medium term (6–18 months) — Integration, automation, and scale readiness
- Objectives:
  - Deep smart‑grid integration: bring in feeder/substation telemetry, outage and SCADA event correlation, and timed meter reads at hourly granularity.
  - Advanced AI forecasting: feeder‑level probabilistic forecasts, short‑horizon (0–24h) and medium‑horizon (1–14d) models; quantile outputs for risk scoring.
  - Mobile app progression: scheduling, inspector performance dashboards, offline sync optimizations, evidence tagging and secure upload.
  - Edge & latency work: deploy lightweight edge aggregators to run inference/ buffering at substations or concentrators.
- Deliverables:
  - `Feeder correlation` module linking alerts to substation events and outage windows.
  - `Predictive scoring` that ranks risk by expected recovered INR, enforcement cost, and legal complexity.
  - `Edge aggregator` prototype for near‑real‑time local scoring.
- Success metrics:
  - AT&C reduction on prioritized feeders: 3–8 percentage points within 6–12 months after full ops cadence.
  - Detection speed: median alert in minutes→hours for streaming events; median alert→inspect ≤48 hours.
  - ROI: positive short‑term ROI on prioritized interventions (recovered INR > intervention cost) in pilot tranches.

Long term (18–36 months) — DISCOM scale & smart‑grid synergy
- Objectives:
  - Full DISCOM rollout by tranches (100k+ meters per tranche) with operationalized inspector programs and central ops center.
  - Smart‑grid orchestration: integrate Helios signals into ADMS/OMS/SCADA workflows for prioritized isolation, outage reduction, and DER coordination.
  - AI forecasting advanced: joint models for load, theft‑risk, and DER impact; use forecasts to optimize procurement and reduce emergency purchases.
  - Mobile suite: full workforce management, SLA tracking, automated ticketing, and regulator‑grade audit trails.
- Deliverables:
  - `ADMS/OMS connectors` and playbooks for automated remediation flows and prioritized switching suggestions (manual or semi‑automated).
  - `Probabilistic planning` tool that simulates EV/solar uptake and projects theft exposure and revenue at scale.
  - `Mobile Suite` enterprise release with role‑based access, offline-first reliability, and integrated evidence ledger.
- Success metrics:
  - AT&C reduction: 8–15 percentage points across targeted feeders over 12–24 months of scale operations (dependent on enforcement capability).
  - Recovered revenue: scale‑dependent (see `docs/impact_metrics.md`) — meaningful contribution to DISCOM cash flow and lower emergency procurement.
  - Detection speed & automation: majority of high‑confidence alerts are auto‑assigned and completed within 72 hours.

Cross‑cutting themes & technical notes
- Governance & ops: strong DISCOM partnership, inspector SOPs, and regulatory alignment are critical; technical work must be matched by process change.
- Data quality & metadata: timestamp sync, timezone handling, ID mapping, and meter health metadata are bottlenecks—invest early in data contracts and test vectors.
- Privacy & security: role‑based access, TLS/mutual auth for MDMS/AMI streams, and tamper‑resistant evidence handling are mandatory for regulatory acceptance.
- Funding & procurement: use staged procurement and performance‑linked financing to reduce capital strain; pilots can be co‑funded by grants or vendor risk‑sharing.

Roadmap milestones (high level)
- Month 0–3: Pilot closeout, Mobile MVP alpha, baseline forecasting integrated.
- Month 3–6: Pilot report, MDMS adapter hardened, initial edge aggregator deployed for selected feeders.
- Month 6–12: Feeder correlation, advanced forecasting models, mobile app v1.0, first tranche planning.
- Month 12–24: Tranche rollouts (100k increments), ADMS/OMS connector pilots, workforce scale‑up.
- Month 24–36+: Full DISCOM operationalization, smart grid orchestration features, procurement optimization capabilities.

Why this vision is realistic
- Incremental: each step builds on validated pilot artifacts and reuses software to lower marginal costs.
- Measured: targets tied to AT&C, recovered INR, and time‑to‑remediate so progress is auditable.
- Aligned: designed to work with Indian DISCOM procurement cycles, mixed meter fleets, and field constraints.

Next steps
1. Approve roadmap and pick short‑term priorities (mobile features, forecasting model scope, and MDMS partners). 2. Prepare a 90‑day sprint plan to deliver the Short‑term milestones and the pilot closeout report.
