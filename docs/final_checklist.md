# Final Checklist — Demo & Judging Readiness

Status key: ✔ = ready; Actions are listed where manual steps remain.

- System working: ✔
  - DB-level E2E test: ✔ (see `backend/tests/test_e2e_flow.py`) — verified locally.
  - Seed data and demo dataset: ✔ (`backend/scripts/seed.py`).
  - Backend service: ready for local demo; use Quick Start in `README.md`.

- Demo flow: ✔
  - Slide deck outline: `docs/slide_deck_outline.md`
  - 3–5 minute timing plan: `docs/demo_timing_strategy.md`
  - Live demo checkpoints and fallback: `docs/demo_fallback_plan.md`
  - Screenshots: `docs/screenshots/` (alert, detail, mobile)
  - Recorded fallback video: place at `docs/demo_assets/demo_60s.mp4` (if not already present).

- Pitch ready: ✔
  - Killer hook: `docs/killer_hook.md`
  - Judge strategy, Q&A & materials: `docs/judge_strategy.md`, `docs/judge_questions_and_answers.md`
  - USPs and competitor comparison: `docs/unique_selling_points.md`, `docs/competitor_comparison.md`
  - Tech justification and deployment strategy: `docs/tech_stack_justification.md`, `docs/deployment_strategy.md`

- Backup ready: ✔
  - Local 60s demo video and 3 screenshots ready to display or share.
  - Data Quality Report template and sample CSV available in `docs/impact_metrics.md` (use for audits).
  - Demo fallback script and Q&A: `docs/demo_fallback_plan.md`

- Team roles defined: ✔
  - Product / PM: owns pilot scope, MoU, and SOW.
  - Engineering lead: deployment, observability, on‑call.
  - Data scientist: model ops, explainability, retraining.
  - Field ops lead: inspector training, evidence collection, enforcement liaison.
  - Legal/compliance: audit trail and regulator coordination.

Pre‑demo checklist (quick run): verify backend health, open demo pages, load screenshots, test mobile app offline queue, and have recorded fallback queued.

Post‑demo followups (automated): collect logs/traces, produce 24‑hour incident report (if any), and upload pilot report to repo.

Last updated: April 9, 2026
