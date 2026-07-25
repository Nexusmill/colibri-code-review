# Colibri review — PatternSkin/__init__.py (bug) — ROUND 2 (targeted: paid re-bill contract)

- **source:** `PatternSkin/__init__.py` (5976 lines; the paid Blender add-on)
- **model:** claude-opus-4-8[1m] (in-session targeted verification)
- **sha256:** `c64c9ba61de44aac0b155c73f77eefa949585adf1c9c30214e9b55ff444716b5` (unchanged since r1)
- **date:** 2026-07-24 · **mode:** bug · ROUND 2 (targeted contract check, not a full re-scan)
- **context pack:** this is the **most-reviewed file in the repo** — r1 hunt (5 confirmed/5 fixed, the
  self-update non-atomic HIGH + 4) plus ~14 prior remediation rows (SVG/XXE, pip concurrency, apply
  pipeline, preview leaks, modal cancel, lithophane guards). Its Replicate transport was extracted to
  `replicate_client.py` (fixed 38e4176). 2 refuted claims on record. The scan is driven by MODAL
  operators (`__init__.py:5413-6190`) that lazily `import ai_parts`.

## Verdict
Targeted money-safety check (the one residual the focused finish flagged): do the paid modal operators
**re-bill** by retrying a per-view paid call now that `ai_parts`/`replicate_client` raise on billed
failures? **No — the re-bill contract is clean.** No new defect. Round rests clean.

## What was verified (the paid re-bill contract) — CLEAN
`PATTERNSKIN_OT_*` AI-scan modal (`modal()` at 5491-5559):
- **No per-view retry.** A per-view `_sam2_masks` failure sets `self._err`; the `wait` phase reports it
  and returns `self._end(context, {"CANCELLED"})` (5519-5522) — the view is NOT re-attempted, so a
  billed failure never re-bills. Combined with the r2 transport fix (the create loop no longer re-POSTs
  on 5xx/timeout/reset), the paid path is money-safe end-to-end.
- **Paid progress is checkpointed per view** (`save_scan_partial`, 5535-5538 / 5550-5553) with the
  comment "a crash now resumes here instead of re-billing"; resume (`load_scan_partial`, 5447-5453)
  reuses finished (paid) views; and a Spector-recognized model reuses a prior scan **FREE** (5459-5476).
- Setup failures surface as `RuntimeError → report → CANCELLED` (5441-5442, 5457-5458) — no silent
  paid retry.

## Not re-reviewed (already covered; out of scope for this targeted round)
- The full 6000-line surface (operators, panel draw, apply/subdivision/projection pipeline, SVG/XXE,
  pip installers, preview/enum caches) — closed across r1 + the ~14 remediation rows; not re-scanned.

## Outcome
- **New defects:** 0. The paid re-bill contract is verified clean; the money-safety story (transport +
  operator) is complete. clean_streak +1. NOT run in a live Blender session (source-traced).
