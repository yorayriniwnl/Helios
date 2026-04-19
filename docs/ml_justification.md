# ML Justification — Why rules alone fail, and why ML helps

Keep it simple and practical.

Why rules alone fail
- Rules are single‑axis and brittle: a threshold that worked on one feeder will misfire on another (different load mix, meter types, or timezones).
- High false positives: naive thresholds flood inspectors with noise, causing fatigue and ignored alerts.
- Stealthy patterns evade rules: coordinated under‑reporting, partial bypasses, or subtle temporal patterns don’t trigger simple checks.
- Heavy maintenance: every new meter vendor, firmware quirk, or seasonal load change requires manual rule updates and tuning.
- Poor prioritization: rules don’t easily rank alerts by expected recovered value, so field effort is spent inefficiently.

Why ML improves detection (practical benefits)
- Learns multi‑feature signatures: ML combines history, local forecasts, neighboring meters, reset events, and metadata to spot patterns rules miss.
- Reduces noise with scores: probabilistic outputs let you gate alerts (high‑confidence vs monitor), cutting false positives sent to inspectors.
- Adapts to change: retraining on labeled inspection outcomes captures new theft modes and firmware/behavior shifts faster than hand‑coding rules.
- Enables ROI prioritization: ML can predict both theft probability and expected kWh/INR, so you dispatch inspections where money returns fastest.
- Explainable enough for ops: use simple explainers (feature attributions, timelines, example fingerprints) so inspectors trust and defend cases.

Practical hybrid pattern (recommended)
1. Start with conservative rules + DQ filters to block obvious bad data and avoid embarrassing demos.
2. Run ML scoring in parallel (shadow mode) to gather labels and calibrate.
3. Promote ML scores to triage once high‑confidence precision is validated (pilot target: ≥85% precision for high‑confidence tier).
4. Keep rules as safety nets (outage windows, meter reset suppression) and for quick debugging.

Operational guardrails (non‑negotiable)
- Confidence + ROI gating: only auto‑assign high‑confidence alerts where expected recovery exceeds inspection cost.
- Human‑in‑the‑loop: inspector labels feed weekly retraining; use calibration so scores map to real precision.
- Audit trail: persist raw inputs, model version, feature values and confidence breakdown for every alert.

Tradeoffs & what to expect
- You need labeled inspections and a short tuning period — expect measurable gains within weeks, not instantly.
- Models require monitoring (drift, data quality) and simple MLOps: versioning, rollbacks, and canarying.
- The hybrid approach limits risk: rules stop obvious mistakes, ML finds the subtle, high‑value cases.

What to tell a skeptical judge (one line)
- "Rules catch the obvious; ML finds the costly, stealthy patterns and scores them so inspectors act only on high‑value, high‑confidence cases." 
