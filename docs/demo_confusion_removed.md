# Remove friction — confusing demo points and simple fixes

Purpose
- Call out the parts of the live demo that commonly confuse judges and give short, plain‑language replacements and a simple 30/60/120s script you can use under time pressure.

Confusing parts (and simple fixes)

- Live trigger & timing risk
  - Confusing: counting into a terminal click, waiting for websockets, or showing verbose terminal output can look brittle if it lags.  
  - Fix: "Count 3–2–1, click, show the updated Action Queue screenshot. If live fails, say 'fallback' and show the prepared screenshot/video immediately." Keep the language: "I’ll trigger an alert now — 3, 2, 1." Pause 0.4s, then click.

- Jargon overload (precision@topK, DQ, hypertables, SHAP, ONNX)
  - Confusing: technical terms lose non‑technical judges.  
  - Fix: Replace with plain phrases: use "high‑confidence results", "automatic data checks", "scales horizontally", and "we can show why a case was flagged on request." Avoid acronyms unless asked.

- Evidence provenance details (hashes, signatures)
  - Confusing: hashing/signing details confuse the narrative.  
  - Fix: Say "signed, auditable photo evidence" and be ready to show the audit slide if asked. Short line: "Photo + signed record = auditable proof."

- Deep model explainability (SHAP/features)
  - Confusing: showing feature graphs wastes time.  
  - Fix: Give a one‑sentence human explanation (e.g., "Why: sudden drop in reported usage and a tamper signal"), and offer a follow‑up deep dive post demo.

- Infrastructure vocabulary (hypertables, partitioning, Kinesis)
  - Confusing: infrastructure details are not persuasive in a pitch.  
  - Fix: Say "scales horizontally and uses optimized time‑series storage" when asked about scale; save architecture slide for technical Q&A.

- Too many numbers or long tables
  - Confusing: judges lose the story in tables.  
  - Fix: Lead with one memorable stat (e.g., pilot payback example) and a single pilot example ("5k meters, 3 months"). Use a clean infographic for the rest.

- Inspector workflow step overload
  - Confusing: step‑by‑step inspector flows get granular.  
  - Fix: Simplify to "one‑tap confirm" and demonstrate with a single tap and the result (evidence captured + closure).

Simplified demo scripts (drop‑in replacements)

30s script (if cut short)
- "Utilities lose X in revenue. Helios finds high‑confidence cases, attaches signed photo evidence, and sends only the best cases to inspectors. Here’s the Action Queue — I’ll trigger one now (3‑2‑1). You’ll see the alert with a photo and a confidence score; the inspector taps to confirm and we record recovered value. Pilot: 5k meters, 3 months."

60s script
- Hook (5s): "Utilities lose X — that’s recoverable revenue." Pause 0.5s.  
- One‑line solution (8s): "Helios: Spot. Seal. Recover — high‑confidence detection, signed evidence, and a one‑tap inspector workflow."  
- Quick demo (30s): Show Action Queue, trigger (3‑2‑1), show alert+photo+confidence, show inspector tap, show recovered figure.  
- Close (7s): "Pilot us for 3 months on 5k meters and we’ll prove the recovery." Pause for questions.

120s script (full short demo)
- Hook (10s): single memorable stat and tagline.  
- Flow (80s): Action Queue → trigger → alert appears → open evidence → inspector confirm → show resulting recorded recovery and retraining note. Use plain language for each step; avoid technical jargon.  
- Close (30s): ROI example, 3‑month ask, and one sentence on scale and safety.

Presenter cues (quick)
- Emphasize one word per sentence (e.g., "revenue", "evidence", "inspect").  
- Pause 0.4–1.0s after the ROI or recovered figure.  
- If any live step fails, acknowledge quickly: "fallback demo" and switch to screenshot/video.

What we changed in the repo
- New concise guide to reduce friction during the demo and give plain‑language scripts for 30/60/120s deliveries.
