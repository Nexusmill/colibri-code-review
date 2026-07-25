# Colibri review — PatternSkin/ai_parts.py (bug) — ROUND 2

- **source:** `PatternSkin/ai_parts.py` (1448 lines; the PAID AI part-scan path — Replicate SAM-2 /
  SAM-3 / Grounding-DINO / grounded_sam / P3-SAM). NOT a twin. Imports bpy → not headless-runnable.
- **model:** claude-opus-4-8[1m] lead verification of a primed **claude-opus** scanner
- **sha256 (reviewed, pre-fix):** `cda83e42a5a6fe32...`
- **sha256 (post-fix):** `7f89c090760177deda7360ab99c6f417adb06eadc83593db668794a88745b895`
- **date:** 2026-07-24 · **mode:** bug · ROUND 2 (the r1 hunt round only reviewed the checkpoint/cache
  block ~140 of 449 lines; **this round covers the previously-unreviewed paid transports**)
- **context pack:** `get_file_outline`; `get_symbol_source` on all 5 create loops; cross-file doctrine
  from the sibling clients' r1/r2 fixes (replicate_client 38e4176, replicate_flux c9c764b — retrying a
  `Prefer:wait` create on 5xx/timeout/reset = double-bill). A prior paid k3 review's 9 candidates used
  as a verification checklist.

## Verdict
One real **HIGH money-safety** defect across **all five** paid transports (the create loop re-POSTed a
possibly-billed prediction on 5xx / timeout / post-send reset) — the exact class already fixed in the
two sibling clients, which the r1 partial scope never reached and the scanner initially dismissed as
"inherent." Fixed + verified (ast-lifted loop: pre 5 POSTs → post 1). 8/9 k3 candidates verified
already-fixed, 1 refuted. One latent guard deferred (AIP-1).

## Findings — Phase-3 dispositions

**[HIGH · FIXED] all 5 paid create loops re-POST a billed prediction on 5xx/timeout/reset** — `_sam2_masks:~215`, `grounding_dino_boxes:~920`, `grounded_sam_mask:~1105`, `sam3_mask:~1197`, `p3sam_start:~1420`
- **What:** each create loop retried `if e.code in (429,500,502,503,504)` **and any `URLError`**. The 4
  `Prefer:wait` transports (and `sam3_mask` is the LIVE "select by name" backbone) bill the prediction
  on receipt, so a 5xx (esp. a 504 gateway timeout), a read-timeout, or a post-send `ConnectionReset`
  (arriving as `URLError.reason`) means it was already created+billed — re-POSTing up to 5× = up to 5
  billed predictions per call. `p3sam_start` (async) likewise, and P3-SAM is the most expensive model.
- **Phase-3:** CONFIRMED. The scanner flagged this only as "inherent, not a code defect"; cross-file
  doctrine (the two sibling clients fixed exactly this as HIGH) proves it IS a fixable code defect.
  Verified via an **ast-lifted** run of the real `grounding_dino_boxes` loop (ai_parts can't import —
  bpy): **pre-fix** HTTP 500 / URL timeout / URL reset → **5** create POSTs each; **post-fix** → **1**
  + a "may have been created and billed; check replicate.com" `RuntimeError`; 429 and
  connection-refused still retry 5× (correct — rejected-before-create / never-sent).
- **Fix:** all 5 loops now retry ONLY `429` + provably-pre-send failures (`ConnectionRefusedError`,
  `socket.gaierror` DNS); `5xx`/timeout/reset raise the billing-warning. (The `_sam2_masks` 422
  first-attempt reprobe is preserved.)

## Already-fixed / refuted k3 candidates (verified against current bytes)
- HIGH duplicate `except HTTPError` (silent 401/402/404) — **fixed** (single handler, non-retryable →
  `RuntimeError`). Normalized-box collapse — **fixed** (`max(abs)<=1.5` scale). p3sam_export selection
  destroy + mesh leak — **fixed** (save/restore + `tmp_mesh` remove). `load_scan_path` unguarded
  np.load — **fixed** (try/except → None). mesh_signature collisions — **fixed/mitigated** (sampled
  sha1 digest folded in). `_load_mask`/`_mask_from_file` temp+image leak — **fixed** (try/finally).
  SSRF/host validation — **fixed** (`_check_fetch_url`/`_check_poll_url` + no-redirect `_urlopen`;
  matches the sibling clients). `render_part_thumbs` negative-polypart wrap — **fixed** (clamp).
- dual-graph `-1` sentinel fuses regions — **REFUTED** (verified: `selectcore.MeshCtx.dual` is built
  only from shared-edge face pairs, so it never contains `-1`).

## Deferred (AIP-1)
- `_text_votes` omits the `ff < nf` id-overflow clamp its 5 sibling visible-face consumers all carry →
  a decoded id ≥ nf (GPU-rounding) would `IndexError` after paid grounding-dino calls. **Latent** — box
  mode (`run_text_select(mode="box")`) is wired to no shipped operator (the live "Select by name" uses
  `sam3_mask`→`_mask_votes`, which IS guarded). One-line clamp banked in AIP-1; not applied because it
  changes an untestable-in-Blender bpy path for an unreachable edge.
- **Residual (noted, not fixed):** a bare `ConnectionResetError` from the create `r.read()` (body of an
  already-created 200) is still uncaught (only HTTPError/URLError caught) — propagates once, no in-loop
  re-bill. Folded into AIP-1.

## Outcome
- **Money-safety defects fixed:** 1 HIGH across 5 transports. **Deferred:** AIP-1. Single file (no twin).
- VERIFIED `junk/_ai_parts_r2_test.py` (ast-lift, buildenv py3.12) pre 5→post 1. NOT run in a live
  Blender session (headless-verified).
