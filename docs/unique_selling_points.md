# Unique Selling Points — Helios

Top 5 USPs

1. Real-time detection and localization:
   - Continuous, low-latency streaming analytics that detect theft signatures (spikes, sustained under‑reporting, bypass patterns) and localize anomalies to feeders or clusters so field teams can act the same day.

2. Explainable AI and evidence-first alerts:
   - Models provide human-readable rationales (feature attributions, event timelines, signature fingerprints) and attach the underlying meter readings and inspection evidence so alerts are defensible in the field and in regulatory contexts.

3. Operator workflow & ROI-driven triage:
   - Built-in alert triage, prioritized worklists, mobile inspection capture, and enforcement cost vs expected recovered‑INR scoring so limited inspection budgets are spent where return is highest.

4. Mixed‑fleet robustness & low‑bandwidth deployment:
   - Designed for India‑style fleets: legacy electromechanical meters, smart meters, intermittent telemetry and lossy comms. Supports edge‑light fingerprinting, local buffering, and graceful degradation where connectivity is poor.

5. Auditable recovery & measurable outcomes:
   - Automatic kWh/INR recovery estimates, pre/post AT&C measurement, immutable audit trails and inspection evidence to close the loop from detection → remediation → verified revenue recovery.

Comparison vs existing systems

- Periodic audits / sample inspections:
  - Detection speed: very slow; misses stealthy localized theft.
  - Explainability: low — investigators often rely on manual evidence gathering.
  - Operator workflow: ad hoc; low automation and poor ROI prioritization.

- Rule‑based thresholding / MDMS alerts:
  - Detection speed: faster but noisy; high false positive rates.
  - Explainability: limited to threshold event logs; little causal context.
  - Operator workflow: point alerts without prioritized triage or built‑in inspector flows.

- Generic anomaly‑detection platforms / ML services:
  - Detection speed: variable; often requires heavy feature engineering and infrastructure.
  - Explainability: often opaque; not designed for field evidence capture or enforcement workflows.
  - Operator workflow: typically absent — integration work is required to make alerts actionable.

Helios advantage: combines low‑latency, explainable models with operational tooling and ROI triage, built specifically for mixed legacy fleets and constrained Indian field conditions — delivering deployable, auditable revenue recovery rather than raw signals.
