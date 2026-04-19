Silent demo mode — run the demo without speaking

What it is:
- A self-running, timed UI walkthrough that shows detection, root cause, remediation, and audit — all on-screen.

How to use (quick):
- If the frontend implements `?demo=silent`, open the app at `http://localhost:3000/?demo=silent` (or your host).
- If not, open the included file `docs/silent_demo_play.html` in your browser — it runs offline and needs no server.

Prep checklist:
- Seed demo data: run `backend/scripts/trigger_demo_alert.py` if needed.
- Open the browser in full-screen and mute the mic; start the slideshow file or the site with `?demo=silent`.
- Optionally record the browser window for a replay fallback.

What the UI shows (no narration required):
- A clear detection headline and severity.
- Root-cause information and impacted services.
- A prioritized, step-by-step remediation card with the highest-impact action highlighted.
- Evidence and an audit trail for judges or reviewers.

Developer notes:
- To integrate into the frontend, add a `demoMode` handler that accepts a `silent` mode, fetches a slide/sequence config, and auto-advances UI states with configurable durations.
- Keep actions non-interactive in silent mode (highlight only) so the demo runs reliably.
