# Data Reliability — Noisy Data, Missing Packets, and Confidence Scoring

Overview
- Reliable detection rests on three pillars: robust ingestion, conservative data sanity handling, and an explicit confidence score that drives operational actions. The goal is pragmatic: reduce inspector workload, avoid enforcement on bad data, and make alerts auditable and reproducible.

1) Ingestion & pre‑flight checks
- Multiple ingest paths: support push (MQTT/webhooks) and pull (MDMS/exports). All ingestion is idempotent (unique key = `meter_id + timestamp`) and recorded to a raw input store.
- Timestamp normalization: convert to UTC, enforce monotonicity per meter, and compute `timestamp_drift = abs(server_time - meter_time)`.
- Deduplication & replay buffer: dedupe on the unique key and hold late arrivals in a short replay buffer (default 15 minutes) so minor network jitter doesn't create false alerts.
- Pre‑flight DQ checks (automated): completeness (% expected reads present), duplicate rate, timestamp drift, and value sanity (no negative kWh, realistic upper bound). Feeder/meter failing DQ are flagged and excluded from enforcement until remediated.

Practical thresholds (configurable defaults)
- Read completeness: pilot inclusion >= 80–85% over the baseline window.
- Timestamp drift: high‑confidence requires median drift ≤ ±2 minutes.
- Replay window: default 15 minutes for near‑real‑time pilots; configurable to 60 minutes where networks are lossy.

2) Handling noisy data
- Detect & flag: use simple deterministic checks first (negative values, non‑monotonic cumulative registers, impossible jumps). Flagged samples are removed from enforcement scoring but retained for diagnostics.
- Smooth & filter conservatively: run a rolling median or Hampel filter to identify single‑sample spikes. For scoring, prefer original data but mark interpolated/smoothed points as lower confidence.
- Firmware/comms noise: detect recurring periodic noise signatures and route meters to a `meter_health` remediation queue rather than immediate enforcement.

3) Missing packets & gaps
- Short gaps (< replay window): wait for late arrivals before scoring; if data arrives, recompute the alert with full window.
- Medium gaps (replay window → few hours): allow conservative scoring only if anomaly magnitude is large and corroborated by feeder‑level signals. Mark alert confidence lower.
- Long gaps (> few hours): mark meter as low‑health and deprioritize for enforcement; add to remediation list for meter/comms repair.
- Interpolation policy: only use linear interpolation for scoring when gaps are short and flagged as such; interpolated values are explicitly tagged and reduce `data_quality_score` contribution.

4) Meter health & data quality scoring
- Per‑meter health is a rolling score (0–1) combining: completeness, timestamp accuracy, read stability, and firmware/comms flags.
- Example formula (normalize inputs 0–1):

```text
meter_health = 0.50 * completeness_score
             + 0.30 * timestamp_score
             + 0.20 * stability_score
```

- Where `completeness_score = min(1, actual_reads/expected_reads)`, `timestamp_score = max(0, 1 - drift_minutes/5)` clamped to [0,1], and `stability_score = 1 / (1 + coefficient_of_variation)` normalized.

5) Confidence scoring (how an alert becomes actionable)
- Purpose: combine model signal with data reliability so field teams act only on high‑value, high‑trust alerts.
- Components (all normalized 0–1):
  - `model_score` — ML anomaly probability or ensemble score.
  - `data_quality` — per‑alert view of read completeness, late arrivals, interpolation, and outlier flags.
  - `meter_health` — per‑meter rolling health score (above).
  - `anomaly_magnitude` — normalized size of deviation vs baseline (larger anomalies get higher score).
  - `corroboration` — feeder/substation signals or neighboring meter agreement.

Example weighted formula (defaults):

```text
confidence = 0.50*model_score
           + 0.20*data_quality
           + 0.15*meter_health
           + 0.10*anomaly_magnitude
           + 0.05*corroboration
```

- Thresholds & operational mapping:
  - `confidence >= 0.80` → High confidence: auto‑assign to inspector (actionable).
  - `0.60 <= confidence < 0.80` → Medium: analyst review / batch assignment.
  - `confidence < 0.60` → Low: monitor, do not assign enforcement tasks.

6) ROI gating & enforcement decision
- Combine confidence with expected recovered INR to form an `action_score = confidence * expected_revenue_inr`. Only alerts with `action_score` above a configured cost threshold are scheduled for inspection. This prevents spending field effort on low‑value recoveries.

7) Explainability & UI representation
- Show a confidence breakdown bar in the alert detail (stacked contributions: model, data quality, meter health, magnitude, corroboration). Show raw inputs and the time‑series window plus any interpolations.
- Show provenance: raw payload, transforms applied, DQ flags, and the snapshot of evidence packaged for inspectors.

8) Active learning & continuous improvement
- Human‑in‑the‑loop: inspector verdicts (true/false/uncertain) feed back as labeled data; retrain weekly during pilot cadence.
- Calibration: calibrate `model_score` to probability space (isotonic or Platt scaling) using labeled inspection outcomes so confidence maps to real precision.
- Threshold tuning: iteratively raise the high‑confidence threshold until desired precision (pilot target: high‑confidence precision ≥ 85% within 4 weeks).

9) Auditability & reproducibility
- Persist raw input, normalized series, DQ flags, computed features, model version, and confidence breakdown for every alert so any alert can be reconstituted and defended in regulatory contexts.

10) Monitoring & SLOs (practical targets)
- Ingestion latency: 95% of reads processed into the detection pipeline within 30 seconds (pilot can be relaxed to 5 minutes if network limited).
- Data completeness: pilot target ≥80–85% for active feeders.
- High‑confidence precision: pilot target ≥85% after first retraining cycles.
- Meter health: reduce low‑health meters by 50% within 6 months via remediation program.

Quick example (numeric)
- Suppose `model_score=0.90`, `data_quality=0.95`, `meter_health=0.90`, `anomaly_magnitude=0.60`, `corroboration=0.80`.
- confidence = 0.5*0.9 + 0.2*0.95 + 0.15*0.9 + 0.1*0.6 + 0.05*0.8 = 0.875 → high confidence (actionable).

What to tell judges (one sentence)
- "We never force enforcement on bad data: every alert carries a transparent confidence breakdown, is gated by ROI, and only high‑confidence alerts are auto‑assigned; inspector outcomes drive fast retraining to raise precision." 

Next steps I can take
- Implement example DQ scripts (completeness, drift, duplicates) in `backend/scripts/` and add the confidence breakdown API for the alert detail panel.
