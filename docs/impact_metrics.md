# Impact Metrics — Measurable Value (Pilot & Scale)

Purpose
- Quantify expected % theft reduction, cost savings, and detection speed for a realistic pilot and show scale implications.

Base assumptions (conservative vs optimistic)
- Pilot size: 5,000 meters across high‑loss feeders.
- Baseline AT&C (targeted feeders): 30%.
- Theft share of AT&C: conservative 50%, optimistic 60%.
- Avg consumption per meter: conservative 150 kWh/month (residential mix), optimistic 300 kWh/month (mixed residential + commercial).
- Retail tariff (used to compute recovered revenue): INR 7/kWh. DISCOM procurement cost: INR 4/kWh.
- Helios recovery (detected & enforced): conservative 40% of theft volume in year 1; optimistic 60% with process maturity.

How we compute key numbers (method)
- Billed energy (B) = meters × avg_kWh_per_month × 12.
- Energy input = B / (1 − AT&C).
- Lost energy L = energy_input × AT&C.
- Theft volume = L × theft_share.
- Recovered_kWh = theft_volume × recovery_rate.
- Gross recovered revenue = Recovered_kWh × retail_tariff.
- Approx net cash gain ≈ Recovered_kWh × (retail_tariff − procurement_cost) − enforcement_costs.

1) Pilot — Conservative scenario
- Inputs: 5,000 meters; 150 kWh/month; AT&C 30%; theft_share 50%; recovery 40%.
- Calculations (rounded):
  - Billed energy (B): 5,000 × 150 × 12 = 9,000,000 kWh/year.
  - Energy input ≈ 9,000,000 / 0.7 ≈ 12,857,143 kWh/year.
  - Lost energy L ≈ 12,857,143 × 0.30 ≈ 3,857,143 kWh/year.
  - Theft volume ≈ 50% × L ≈ 1,928,571 kWh/year.
  - Recovered_kWh ≈ 40% × theft ≈ 771,429 kWh/year.

- Metrics (conservative):
  - % theft reduction: 40% of theft volume recovered (by design of the scenario).
  - AT&C change: absolute reduction ≈ Recovered_kWh / energy_input ≈ 771,429 / 12,857,143 ≈ 6 percentage points (30% → 24%).
  - Gross recovered revenue ≈ 771,429 × INR 7 ≈ INR 5.4M (~INR 54 lakh) per year.
  - Net cash margin (approx) ≈ 771,429 × (7 − 4) − enforcement_costs. Example: if enforcement_costs ≈ INR 1.0M, net ≈ INR 1.31M/yr.
  - Detection speed: median time‑to‑alert (streaming) ≪ 24 hours; median time from alert → assigned inspection ≈ 24–72 hours.

2) Pilot — Optimistic scenario
- Inputs: 5,000 meters; 300 kWh/month; AT&C 30%; theft_share 60%; recovery 60%.
- Calculations (rounded):
  - Billed energy (B): 5,000 × 300 × 12 = 18,000,000 kWh/year.
  - Energy input ≈ 18,000,000 / 0.7 ≈ 25,714,286 kWh/year.
  - Lost energy L ≈ 25,714,286 × 0.30 ≈ 7,714,286 kWh/year.
  - Theft volume ≈ 60% × L ≈ 4,628,571 kWh/year.
  - Recovered_kWh ≈ 60% × theft ≈ 2,777,143 kWh/year.

- Metrics (optimistic):
  - % theft reduction: 60% of theft volume recovered.
  - AT&C change: absolute reduction ≈ 2,777,143 / 25,714,286 ≈ 10.8 percentage points (30% → ~19.2%).
  - Gross recovered revenue ≈ 2,777,143 × INR 7 ≈ INR 19.4M (~INR 1.94 Cr) per year.
  - Net cash margin (approx) ≈ 2,777,143 × (7 − 4) − enforcement_costs. Example: if enforcement_costs ≈ INR 2.0M, net ≈ INR 6.33M/yr.
  - Detection speed: real‑time alerts (minutes→hours), assignment & remediation window 24–72 hours (depends on field capacity).

3) Scale example (100k meters at 300 kWh/month, conservative recovery)
- Quick result (rounded): recovered_kWh ≈ 30.86M kWh/year → gross ≈ INR 216M/year (≈ INR 21.6 Cr); net margin ≈ INR 92.6M/year (≈ INR 9.26 Cr) at a 3 INR/kWh margin.
- Ballpark payback: if tranche cost ≈ INR 45 Cr per 100k meters (procurement + install), payback ≈ 45 Cr / 9.26 Cr ≈ 4.9 years (sensitivity to local tariffs and procurement cost).

Detection speed (operational impact)
- Typical manual/manual‑trigger detection: 30–90 days (scheduling, audits, and follow‑ups).
- Helios (streaming + triage): median time‑to‑alert < 24 hours; median time‑to‑inspect 24–72 hours; faster detection compresses the window to intervene, reducing cumulative losses and lowering enforcement costs per recovered INR.

Key takeaways
- Software‑first pilots (existing telemetry) can show positive short‑term ROI because integration & cloud costs are small; payback can be months if data coverage exists.
- Hardware‑heavy pilots (bulk smart‑meter procurement) have larger upfront costs; payback is multi‑year but scale economics and avoided emergency procurement make the investment attractive at DISCOM scale.
- Helios delivers measurable outcomes: single‑digit to low‑double‑digit percentage‑point AT&C reductions on targeted feeders within 6–12 months and meaningful recovered revenue that compounds with process maturity.

Notes & caveats
- All numbers are illustrative and sensitive to local consumption mix, tariff structure, theft composition, enforcement effectiveness, and contract costs. Use local baseline meter reads and DISCOM procurement/billing figures to re-run this sheet for a specific pilot city.

Want a one‑page XLS with these inputs so you can plug local numbers? I can generate a downloadable CSV/XLS template with formulas.
