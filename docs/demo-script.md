# Helios — Demo Script

Total time: ~3 minutes

## Problem (30s)

What to say (30s):

"Today, grid operators face two big pain points: noisy alerts that bury real incidents, and slow, manual triage when something goes wrong. That delays detection and increases outage impact. In many systems, teams only become aware after an incident escalates or a customer reports it — often hours later."

Key bullets to call out:
- High latency from anomaly -> action
- Too many false positives / low signal-to-noise
- Hard to correlate across meters and geography

## Solution (30s)

What to say (30s):

"Helios ingests meter readings in real time, applies lightweight rules plus ML-assisted scoring to prioritize alerts, and surfaces everything on a single, interactive dashboard. We add geospatial context with a heatmap so operators can spot hotspots at a glance and drill down to affected meters in one click."

High-level capabilities to name:
- Realtime alerts (WebSocket + REST)
- Heatmap + zone drill-downs
- Per-meter usage charts and anomaly history
- Demo mode for reproducible demo data

## Live demo steps (2–3 minutes)

Preparation: open the dashboard at `http://localhost:3000`. If you don't have live backend data, toggle **Demo** in the top-right to ON — the app will reload and start streaming synthetic readings and alerts.

Step 1 — Quick orientation (20s)
- Show top-left KPIs (total meters, alerts, readings). "These are live KPIs updating as data streams in."
- Point to the top-right Demo toggle. If demo is off, enable it now.

Step 2 — Heatmap & hotspots (30s)
- Move to the Zones card with the map. Explain the color gradient: green → red indicates low → high risk.
- Highlight a red hotspot. "This heatmap aggregates anomaly density across zones so you can prioritize where to look first."

Step 3 — Drill-down (30s)
- Click a hotspot / zone to open the right-side panel. Show metrics: meters, alerts, anomaly density, and top meters.
- Open a top meter from the list. In the meter detail view, show the Consumption chart and the Recent Anomalies pane. "Here you can see the anomaly timeline and exact readings that triggered the alert."

Step 4 — Live alerts & triage (30s)
- Return to the dashboard and watch the Live Feed. With demo mode on, alerts will appear automatically every few seconds.
- Click a critical alert to show details (explain severity and affected meter). Emphasize how fast an operator can see context and decide (escalate, assign, resolve).

Step 5 — Wrap up visual proof (20s)
- Re-open the heatmap and show how alerts concentrate geographically. "You can export, assign, or drill into logs from here."

Timing note: most steps are automated by demo mode; if you want to force an example, toggle demo off/on or open the browser console and run `localStorage.setItem('helios.demo','1'); location.reload()`.

## Impact (30s)

What to say (30s):

"Helios reduces time-to-detect from hours to minutes by streaming anomalies and prioritizing them with a risk score. Operators spend less time hunting and more time resolving — that translates directly to fewer outages, faster SLA response, and lower operational cost. For a pilot, we can seed your meters into the demo engine and show your team a 15–30 minute deep-dive."

Closing / Ask:
- Request a 1-hour pilot with sample meter data, or offer a follow-up demo tailored to their topology.

---

Notes for presenter:
- Keep each section crisp. Use the Demo toggle early to avoid waiting for live data.
- Emphasize a single-sentence value prop after the live demo: "Find problems faster, act with context." 
