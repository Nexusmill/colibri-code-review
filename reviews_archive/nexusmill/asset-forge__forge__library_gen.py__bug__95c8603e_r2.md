# Colibri review — asset-forge/forge/library_gen.py (bug) — ROUND 2

- **source:** `asset-forge/forge/library_gen.py` (+ twin `asset-forge-user/forge/library_gen.py`)
- **model:** claude-opus-4-8[1m] lead verification of a primed **claude-sonnet** scanner
- **sha256 (reviewed, pre-fix):** `95c8603eb5fe5900e9647d789139bb0b79c0dd675b673ed0cf07e7a3dac142af`
- **sha256 (post-fix):** `448a8345f1331e5cd9a5deba2812b5638f496f437b4cd934ab24570598ba0c0b`
- **date:** 2026-07-24 · **mode:** bug · ROUND 2 (DELTA vs r1 fable-5-max review `ca942a8c`)
- **context pack:** `get_file_outline`; call sites of `estimate`/`build_plan`/`prepare_job` via
  `search_text` in app.py — `libgen_estimate` (app.py:849-852) calls `build_plan` + `estimate` with
  **no** try/except; the model comes from `d.get("model","flux-schnell")` (UI dropdown, but
  unvalidated server-side). r1 fixed the unclamped **count** (MAX_COUNT_PER_TYPE=200) + reconciled
  the twin; LG-1/LG-2 deferred.

## Verdict
Two **reachable** defects found and fixed (money-safety price gap + malformed-`types` 500); the
scanner's CRITICAL was verified real but **downgraded to MEDIUM** in Phase-3 (single-user localhost
self-key app; model normally arrives from a catalog dropdown → trigger needs a crafted/malformed
request). One latent item deferred. Twins byte-identical after fix.

## Findings — Phase-3 dispositions

**[CRITICAL→MEDIUM · FIXED] Off-catalog `model` → $0 estimate + $0 spent_est for a billed run** — `line 162`, `302-303`
- **What/Trigger:** `estimate()` did `m = cat["models"].get(model) or {}` → `price 0.0` for any model
  not in `catalog.json`. `/api/library_gen/estimate` (and `spent_est` during the run via the same
  fallback at 302-303) therefore reported **$0.00** while a real Replicate generation billed the
  user's account. app.py does no model validation; `ReplicateProvider` only regex-checks the slug
  *shape*, not the priced allowlist.
- **Phase-3:** CONFIRMED the $0 pricing path end-to-end. **Downgraded CRITICAL→MEDIUM:** it is the
  user's own key on localhost and the model normally comes from a catalog-populated dropdown, so the
  live trigger is a crafted/malformed/stale-client request, not an external attacker. The fail-closed
  guard is still correct doctrine (G16 AI-key honesty, G19 price-on-control, G3 fail-closed).
- **Fix:** `estimate()` raises `ValueError` if `model not in cat["models"]`; `prepare_job()` now
  computes model+estimate **before** `out_dir.mkdir()` so an unpriced model is rejected with **no
  orphan job dir**. VERIFIED pre 3/7 → post 7/7.

**[LOW · FIXED] malformed `types` → uncaught `TypeError`/500** — `line 94-96`
- `set(want)` with no shape check: `types: 5` → `'int' not iterable`; `types: [{...}]` → unhashable
  dict. CONFIRMED (app.py doesn't wrap it). Restructured the branch to reject non-list **and**
  list-of-unhashable with a clean `ValueError`, mirroring the adjacent count guard. VERIFIED both.

**[LOW · DEFERRED LG-3] `lock_palette` falsy-collapse** — `line 143,147`
- `locked_pal or rng.choice(pals)` re-rolls if a palette value is ever falsy (`""`). **Not reachable**
  — catalog palettes are all non-empty strings (PLAUSIBLE, latent). One-line patch banked in LG-3.

## Missing safeguards / follow-ups
- **app.py (unit 13):** `libgen_estimate`/`libgen_start` return a **500** on these `ValueError`s
  (and on `build_plan`'s existing ones) instead of a clean **400**. Fail-closed is preserved (no paid
  run launches), but wrapping those two endpoints to return 400 is a UX follow-up for the app.py unit.
- LG-1 (flux-1.1-pro-ultra priced-but-unmapped) and LG-2 (no manifest on pause) re-confirmed still
  open; not re-charged.

## Outcome
- **Live defects fixed:** 2 (money-safety price guard + orphan-safe reorder; types 500). **Deferred:** LG-3.
- **Twin parity:** reconciled byte-identical; `sync_builds.py` → *builds in sync*.
- **Not run in a live Flask session** — headless-verified (buildenv py3.12).
