# Demo Fallback Plan — API / UI Failures and What to Say

Purpose
- Short, calm scripts and immediate steps for presenters to recover a demo if the API or UI fails. Keep the audience confident, switch to a fallback, and promise clear follow‑up.

Immediate presenter opening (30s)
- Say: "We’ve detected a transient issue with the live demo. I’ll switch to our recorded/slide fallback and we’ll continue — I’ll share an incident report within 24 hours." Pause 1–2s, then switch to fallback assets.

If the API fails (backend errors, timeouts)

What to say (one line)
- "The backend is experiencing a transient error; we have a verified 60s recorded demo that shows the exact same flow — I’ll play that now and continue the Q&A. We will deliver logs and a 24‑hour incident summary." 

Immediate actions (presenter)
1. Play the 60s recorded demo (local file or hosted video) that mirrors the live flow. Have this ready in `docs/demo_assets/` or locally.
2. Show 2 screenshots: prioritized alert list and alert detail (use `docs/screenshots/`).
3. Offer to show raw evidence: time‑series CSV/JSON and inspection photos (hosted or in repo) to prove results are auditable.
4. Promise immediate follow‑up: collect request IDs/traces and provide an incident report within 24 hours and a targeted fix timeline (72 hours) if needed.

Technical quick recovery (ops)
- Check health endpoints and logs (`/health`, container logs). If safe, restart the backend service. If no live recovery, switch UI to static demo mode that serves precomputed JSON (local fallback) and resume.

If the UI breaks (rendering errors, missing assets)

What to say (one line)
- "The front‑end is not rendering correctly in this environment — we’ll play a short recorded UI walkthrough and continue; the detection and audit logic runs server‑side and is fully auditable." 

Immediate actions (presenter)
1. Open the fallback slide with screenshots or a short recorded UI video (60–90s). 
2. Narrate the clicks: highlight the alert, the explainability panel, and the mobile evidence flow using screenshots. 
3. If needed, open the inspector evidence packet (photos, geo, timestamp) to show auditable proof.

If data looks inconsistent or questionable during demo

What to say (one line)
- "We run a quick Data Quality Report before enforcement. If this dataset doesn’t meet thresholds, we exclude it and will show the validated dataset instead — here are the DQR results." 

Immediate actions
- Show the precomputed Data Quality Report (read completeness, timestamp drift, duplicates). If poor, switch to the validated demo dataset and explain why the quality gate exists.

Fallback explanation to judges (confident, transparent)
- Be honest and own it: "This is our live demo fallback — the recorded flow uses real (or realistic) pilot data and an auditable trail. We will deliver logs, a root‑cause summary within 24 hours, and a remediation plan within 72 hours." 

One‑line Q&A replies (copy‑paste)
- API failure: "We have a verified 60s recorded demo and will provide logs and an incident report within 24 hours." 
- UI break: "We’ll play the recorded UI walkthrough; the backend detection and audit trail remain intact and auditable." 
- Data quality: "We run a mandatory pre‑flight DQR and only enforce where quality meets thresholds; if this dataset fails, we’ll show the validated one." 

Presenter checklist (before demo)
- Prepare a 60s recorded demo video and place in `docs/demo_assets/` (or local drive).
- Keep 3 screenshots in `docs/screenshots/` (alert list, alert detail, mobile evidence).
- Have the Data Quality Report and a sample CSV available for quick sharing.
- Ensure at least one team member can access logs/traces for post‑demo investigation.

Tone & guidance
- Stay calm, state the fallback, play the recorded flow, continue with the narrative, and promise a short, concrete follow‑up (24h incident report, 72h fix plan). Judges value transparency and a reliable remediation timeline more than uninterrupted demos.
