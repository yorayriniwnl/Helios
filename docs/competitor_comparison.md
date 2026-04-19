# Competitor Comparison — Feature vs System

| Feature | Helios (our system) | Traditional meters | Manual inspection |
|---|---|---|---|
| Real‑time detection | Yes — streaming, low‑latency detection and localization to feeders/clusters (minutes→hours). | No — mechanical meters only record cumulative registers; no streaming detection. | No — inspections are periodic; detection latency is days→months. |
| Explainable AI | Yes — feature attributions, event timelines and signature fingerprints, with attached raw readings and evidence for field defensibility. | No — no AI layer or explainability; only raw reads. | Partial — human explanation possible but not standardized or data‑driven. |
| Operator workflow & triage | Yes — prioritized worklists, ROI scoring, mobile inspection capture and integrated audit trail. | No — requires separate systems to manage field ops. | Partial — established workflows exist but are manual, inconsistent, and low automation. |
| ROI-driven prioritization | Yes — expected recovered‑INR × probability vs enforcement cost to maximize inspection ROI. | No — no automated prioritization. | Not systematic — inspectors are guided by plans or experience, not automated ROI. |
| Mixed‑fleet robustness | Yes — built for legacy and smart meters, intermittent telemetry, and lossy comms with edge buffering. | Varies — many legacy meters have no comms; smart meters depend on vendor features. | N/A — inspections can target any meter but are sample‑based and low coverage. |
| Low‑bandwidth / edge support | Yes — edge‑light fingerprinting and local buffering for constrained Indian field conditions. | No — legacy meters lack edge analytics. | Not applicable. |
| False positives / noise | Lower — closed‑loop operator feedback and model tuning reduce noise and focus field effort. | N/A (no automated alerts) | Can be high operational noise if sampling thresholds aren’t well targeted. |
| Auditability & evidence | High — time‑series, photos, inspection logs and immutable trails for regulatory/operational validation. | Low — limited to register reads; little attached evidence. | Medium — inspectors can collect evidence, but formats and retention vary. |
| Time to actionable alert | Minutes–hours (streaming + triage) | None | Days–weeks (scheduling and travel) |
| Scale & marginal cost | Low marginal cost to scale inspections; software targets only high‑value remedials. | Low hardware cost but no detection; losses persist. | High operational cost per inspection; not scalable for continuous coverage. |

**Summary:** Helios combines real‑time detection, explainable AI, ROI‑driven triage, and field‑ready workflows built for mixed legacy fleets and low‑bandwidth Indian conditions. Traditional meters and manual inspection are essential infrastructure or processes but cannot deliver continuous, auditable, high‑ROI detection at scale — Helios is designed to fill that operational gap and produce measurable recovered revenue and reliability gains.
