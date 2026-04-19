# India Context — Grounded Examples for the Pitch

Purpose
- Provide three concrete, India‑specific examples (summer overload, night theft, dense urban transformers) with short descriptions and suggested pitch lines to make the problem and solution feel immediate and local.

1) Summer overload (urban cooling)
- What it looks like:
  - During peak summer days, urban feeders and transformers approach capacity; legitimate consumption spikes (cooling, commercial loads) make simple thresholds noisy.
  - Theft often increases as overloaded equipment and poor voltage regulation make tampering easier and harder to detect.
- Why it matters:
  - High load periods are when the value of recovered kWh is highest (procurement costs spike) and outages are most damaging.
- How Helios handles it:
  - Short‑horizon forecasts (0–24h) establish expected diurnal baseline; anomaly detection flags deviations beyond forecast uncertainty bands.
  - Prioritize alerts that exceed both anomaly magnitude and expected INR recovered, so teams act where marginal benefit is highest.
- Suggested pitch line:
  "In summer, our forecasts separate real cooling load from theft — we only flag deviations outside the forecast band, so inspectors act on the real money, not seasonal noise."

2) Night theft (stealthy under‑reporting)
- What it looks like:
  - Meters show normal daytime readings but sustained under‑reporting during night hours; often coordinated across a cluster or tied to bypass devices.
  - Hard to catch in periodic audits because sampling misses the sustained low‑report windows.
- Why it matters:
  - Night theft accumulates silently and compounds into large annual losses; detection often yields high kWh and INR per inspection.
- How Helios handles it:
  - Detect persistent nocturnal deviations using hourly baselines and neighbor corroboration (nearby meters/feeder behavior).
  - Use explainability to surface the exact night‑hours signature and evidence timeline for inspectors.
- Suggested pitch line:
  "We find the thieves who steal at night — a handful of night‑time under‑reporting alerts in one feeder can pay for a full tranche of inspections." 

3) Dense urban transformers (localized high losses)
- What it looks like:
  - A single transformer or feeder in a dense urban pocket (markets, informal settlements) shows much higher losses than neighbors.
  - Causes include unmetered connections, meter tampering, and feeder bypasses; field verification is logistically heavy but high value.
- Why it matters:
  - Localized interventions can recover large kWh quickly and improve reliability for many customers served by the transformer.
- How Helios handles it:
  - Localize anomalies to transformer/feeder clusters using spatial aggregation, and produce a prioritized list of meters + suggested inspection routes to minimize travel cost.
  - Package inspectable evidence (time series, photos, neighbor comparisons) so field teams act fast and decisively.
- Suggested pitch line:
  "Target the single transformer that leaks revenue — a focused campaign there recovers value fast and reduces outages for thousands of customers."

Integrate into pitch
- Where to mention: slide 2 (Problem), slide 6 (How it works — show one example flow), and slide 7 (Demo — trigger a night‑theft or transformer alert during the wow moment).
- Demo tactic: trigger the `demo-shock-0001` payload with coordinates near a dense urban marker, then switch to the mobile inspector route that shows several nearby meters flagged — visualizing a route reduces cognitive load and makes the impact immediate.

Quick copy for presenter (30–45s)
"In City X we see three repeatable patterns: summer overloads that mask theft during peak cooling, stealthy night‑time under‑reporting that silently accumulates loss, and dense urban transformers where a single feeder can leak crores. Helios separates demand from theft with short‑horizon forecasts, localizes anomalies to feeders, and sends prioritized, evidence‑packed routes so inspectors recover revenue fast." 

Files to include in deck
- Add `docs/india_context.md` to Appendix and reference in slide notes; add the three short pitch lines to the speaker notes for slides 2, 6 and 7.
