# Demo "Shock" Moment — instant, urgent, and undeniable

Goal
- Create a single demo moment that feels realtime and urgent — a sudden anomaly appears, the UI flashes, a chime plays, and the alert is instantly actionable so judges react with "ohhh damn".

Outcome (what judges must see)
- An unexpected, high‑confidence alert appears on the dashboard in real time.
- The alert row and map marker get a dramatic pulse and spotlight.
- A short, clear data card shows expected recovered kWh and recovered INR (big number).
- Quick one‑click assignment pushes the case to the inspector flow and updates the KPI panel.

Prep (assets to create before the demo)
- `docs/demo_assets/critical_alert.json` — prebuilt alert payload (included in repo). Replace fields with local pilot values if desired.
- Screenshots: alert list, alert detail, mobile evidence (place in `docs/screenshots/`).
- Optional chime: local file `docs/demo_assets/alert_chime.mp3` or use the hosted fallback chime URL in the instructions.
- A short recorded fallback video (60s) that mirrors the live steps (recommended).

Execution (operator steps)
1. Start the demo showing the calm dashboard and explain the flow for 45–60s.
2. When ready for the wow moment, run the trigger script:

   ```bash
   python backend/scripts/trigger_demo_alert.py --mode post --backend http://localhost:8000
   ```

   - `--mode post` will attempt to POST the prebuilt `critical_alert.json` to a demo endpoint on the backend.
   - If your backend does not expose a demo endpoint, run with `--mode file` to write the alert JSON to disk and use the console fallback below.

3. Immediately after running the trigger, paste the console highlight snippet into the browser dev console (or bind it to a small bookmarklet). This creates the pulse + audible chime and scrolls the alert into view.

Console highlight snippet (copy → paste into browser console)

```javascript
(function(){
  // CSS pulse
  var s=document.createElement('style');
  s.innerHTML = `@keyframes heliosPulse{0%{transform:scale(1)}50%{transform:scale(1.02)}100%{transform:scale(1)}} .helios-shock{animation:heliosPulse 1.2s ease-in-out infinite;box-shadow:0 0 18px 6px rgba(255,60,60,0.85);border-left:6px solid #ff3b30;}`;
  document.head.appendChild(s);

  // locate alert by known demo id and highlight
  var id = 'demo-shock-0001';
  var el = document.querySelector('[data-alert-id="'+id+'"]') || document.querySelector('#alert-'+id) || document.querySelector('.alert-row[data-id="'+id+'"]');
  if(el){ el.classList.add('helios-shock'); el.scrollIntoView({behavior:'smooth', block:'center'}); }

  // play a short chime (fallback to public chime if local not available)
  var audio = new Audio('https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg');
  audio.volume = 0.9; audio.play().catch(()=>{});
})();
```

What to say (scripted lines)
- Before trigger: "We monitor feeders in real time but normally show only high‑value alerts to avoid noise. Watch what happens when a true theft signature appears." (pause)
- Trigger line: run the script and say: "There — that just happened in the field." Pause for judges reaction.
- Then: "This alert estimates ~1,500 kWh and ~₹10,500 recoverable — inspector assigned and verification in progress." Click assign.

UI dramatics (optional extras)
- Map ping: add a brief red pulsing marker around the alert's GPS coords.
- KPI flash: temporarily animate the top KPI card (e.g., recovered INR increment) with a quick plus overlay.
- Inspector push: if mobile is connected, demonstrate the inspector push arriving within seconds.

Fallback (if streaming / real‑time path is unavailable)
- Run the script in `--mode file`, then paste a short snippet in the console to load `docs/demo_assets/critical_alert.json` into the UI live list:

```javascript
fetch('/docs/demo_assets/critical_alert.json').then(r=>r.json()).then(alert=>{
  // adapt to your UI: insert `alert` into the list and open the detail panel
  window.__demo_inject_alert && window.__demo_inject_alert(alert);
  console.log('Injected demo alert');
});
```

Technical notes (for engineers)
- We recommend adding a temporary demo route on the backend (disabled by default) for staging demos: POST `/demo/trigger_alert` which ingests a single alert payload and broadcasts it on the existing notifications channel (websocket/SSE). The trigger script attempts to POST there.
- Keep demo mode disabled in production; protect demo endpoints by a local secret key.

Timing
- Calm walkthrough: 45–60s. Trigger → visual shock: immediate (0–3s). Reaction + assign: 20–40s. Conclusion & KPI update: 20–30s.

Ethics & reality signal
- Label this as a staged demo but use real pilot data formats and accurate ROI numbers. Judges value honest, auditable demos — the shock moment should be real data shaped to be visually impressive, not fabricated numbers.

Files added in repo
- `backend/scripts/trigger_demo_alert.py` — small helper to POST or write the demo alert.
- `docs/demo_assets/critical_alert.json` — the alert payload used by the trigger.
- `docs/demo_shock_moment.md` — this design doc and operator script.

End of design.
