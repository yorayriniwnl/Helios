Silent demo mode — run the demo without speaking

What it is:
- A self-running, timed UI walkthrough that shows detection, root cause, remediation, and audit — all on-screen.

How to use (quick):
- Open the app at `http://localhost:3000/?demo=silent` (or your host) — it redirects to the dashboard and starts automatically.
- Offline fallback with no server at all: open the included file `docs/silent_demo_play.html` directly in a browser.

Prep checklist:
- No manual seeding needed — silent mode runs entirely on the built-in demo data engine (frontend/lib/demo.ts), the same one the "Live demo" toggle uses.
- Open the browser in full-screen and mute the mic; the tour advances itself.
- Optionally record the browser window for a replay fallback.

What the UI shows (no narration required):
- A clear detection headline and severity (Anomaly Detected).
- Root-cause information and a confidence/recovery estimate (Prioritization).
- Assignment to an inspector (Assignment).
- Evidence capture (Evidence Capture).
- Resolution and recovered value (Recovery).

Implementation notes:
- `?demo=silent` on any page redirects to `/dashboard?demo=silent`; `GuidedDemo` (frontend/components/ui/GuidedDemo.tsx) reads that param on mount and auto-starts the same timed tour the "Start Demo" button triggers manually.
- Each step highlights one `data-demo-id` target, shows an on-screen instruction card, and self-advances after a fixed duration — no clicks required once started.

