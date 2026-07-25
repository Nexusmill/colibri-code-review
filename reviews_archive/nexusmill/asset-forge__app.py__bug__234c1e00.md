# colibri-review — asset-forge/app.py — bug (hunt round 1, effort=high) [+ byte-identical twin]

- **Source:** asset-forge/app.py (byte-identical twin asset-forge-user/app.py, G23) · **Scanner:**
  general-purpose subagent @ claude-opus (deep) · **Verification + partial fix:** claude-opus-4-8[1m]
  (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 234c1e00f1a6e2c390652728d955dfd75adbd5bd54d48ea3f4b5d40f48edd3d8 (1121 lines);
  **post-fix:** 917df447
- **Date:** 2026-07-23 · **Mode:** bug · round 1, DELTA over two prior reviews (K3 @6b58ccc3;
  in-session @dcff7220). Only change since dcff7220 was the `/api/verify` mkstemp fix.
- **Context pack:** prior reviews + remediation rows; refuted ledger empty at dispatch. Traversal
  guards (`_safe_under_output` resolve-based), origin guard (127.0.0.1 + Host/Sec-Fetch/Origin/
  Referer), count clamps, `_REG_LOCK` evict-then-insert all adversarially traced and hold.

## Verdict
Heavily hardened. No new HIGH/CRITICAL or new money-safety defect. One safe mechanical LOW fixed
this round; the rest (one new availability LOW + four **confirmed-open carryover MEDIUMs** from
dcff7220 that were never remediated) are recorded as this file's **round-2 backlog** — they need a
Flask test harness or careful concurrency/security work not to be rushed. app.py stays active.

## Fixed this round
**[LOW] `null` request body → 500 on five `force=True` endpoints lacking the `or {}` guard** -
`preview:439`, `generate:453`, `bundle_start:778`, `libgen_estimate:870`, `libgen_start:900`
- What: these used `request.get_json(force=True)` (no `or {}`), so a `null` body → `None.get(...)`/
  `d[...]` → uncaught 500 that runs the full error-report writer. The sibling endpoints
  (`token_*`, `settings`, `output_delete`, …) already use `… or {}` — an internal inconsistency.
- Fix: `… or {}` at the five sites (matches the existing pattern). The 8-space-indented
  `libgen_control` site (980) was left as the scan verified it's dict-guarded upstream.
- Verify: py_compile clean, 0 double-guards, exactly 1 bare site remaining (the excluded one);
  mirrored to the twin, `sync_builds.py` green. NOT exercised via a live Flask request (inspection +
  compile only) — the change is a one-token match of six existing call sites.

## Round-2 backlog (CONFIRMED open, NOT fixed this round — verify against current bytes then fix)
- **[MEDIUM] Raw `str(exc)`/`traceback` bypass `_redact`** on job surfaces + disk — `_error_payload:211`,
  `_run_bundle` `trace=`:769, `_run_libjob` pause_reason:889/892. Secret-leakage; route through
  `_redact`. (Security — do in round 2 with a `_redact` unit test.)
- **[MEDIUM] Chosen reference silently dropped from a paid bundle** — `_run_bundle:727-731`:
  `reference_data_uri(rid)` → None for an id absent from userlib `_INDEX` → `ref_cat`/`ref_random`
  cleared → run proceeds unreferenced, no warning. (Money/quality — at least warn.)
- **[MEDIUM] `output_delete` refuses FINISHED (not just running) job dirs** — active-set at 1071-1072
  collects `v["dir"]` regardless of status.
- **[MEDIUM] Non-atomic libgen resume race** — `libgen_control` resume (973-984) outside `_REG_LOCK`;
  two concurrent resumes both spawn `_run_libjob`, loser's `_RunLock` RuntimeError flips a live job
  to "error". (Concurrency-subtle — fix under the lock, test carefully.)
- **[LOW] Registry lock held across disk I/O in `_evict_finished_lib`** (:912→930) — snapshot dead
  dirs, release lock, then `load_job` outside it. (Availability on a slow library share.)
- **[LOW] Non-string body fields → `(123).strip()` 500** on the same five endpoints — `str()`-coerce
  before `.strip()` (companion to the `or {}` fix above).
- Several dcff7220 LOWs still open (verify tracer language, `hf_` in `_SECRET_RE`, `_publish_to_library`
  contract/comment drift).

## Fixed since last review (verified, not re-reported)
- Library-gen unbounded paid spend (dcff7220 #1) → clamped `MAX_COUNT_PER_TYPE=200` in library_gen.
- `_verify_one` temp-leak + `/api/verify` 500 on non-image → `finally: unlink(missing_ok=True)`.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- `libgen_control` resume whole-body-null 500 — the resume branch only runs on a dict body with
  `action:"resume"`; a null body falls to `else → 400`.
- `_safe_under_output` absolute-path/symlink escape — `.resolve()` collapses symlinks and an absolute
  relpath resolves outside OUTPUT, failing the `base in p.parents` check.
- `zip_selected` traversal via `names` — `/`/`\` filtered + each entry re-checked with `resolve()`.
