# colibri-review — asset-forge/app.py — bug (hunt ROUND 2, effort=high, PRIMED scanner) [+ twin]

- **Source:** asset-forge/app.py (byte-identical twin, G23) · **Scanner:** general-purpose subagent @
  claude-opus, **primed with the full G6/no-grep canon** (its trace: "Navigation via jCodemunch only …
  No grep") · **Verification + fix:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** 917df447dc30a57301b7234939ed5e8665422e17296ab662028a052feb61226b (unchanged since r1)
- **Date:** 2026-07-24 · **Mode:** bug · ROUND 2 (targeted the r1 recorded backlog + a deeper hunt).

## Verdict
Round 2 re-verified all four r1-backlog MEDIUMs against current bytes and added two LOWs. The
**security** one (raw exception text bypassing `_redact` onto the UI *and disk*) is fixed this round;
the concurrency/lock MEDIUMs are recorded for a focused round 3 (they want careful, tested changes).

## Fixed this round
**[MEDIUM] Unredacted `str(exc)`/traceback leaks to job surfaces AND disk** - `_error_payload:211`,
`_run_bundle:769`, `_run_libjob:889/892`
- `_error_payload` returned `"error": str(exc)` unredacted (only `report` was redacted); `_run_bundle`
  persisted `trace` + `error` into `BUNDLE_*.job.json` (replayed by `bundle_history`); `_run_libjob`
  wrote `pause_reason=str(e)[:200]` unredacted to the entry and the job file. A provider exception
  embedding a token (`r8_`/`sk-`/`gsk_`/`Bearer …`/`AKIA…`) leaked to the UI and to disk. **Fixed:**
  every raw-exception surface routed through `_redact`. **Verified:** pre-fix the token leaked in
  `_error_payload['error']`; post-fix `[REDACTED]` (junk/_appredact_test.py 6/6, pre-fix 5/6).

## Round-3 backlog (CONFIRMED open this round — NOT fixed; verify current bytes then fix)
- **[MEDIUM] Chosen paid reference silently dropped** - `_run_bundle:727-731`: `reference_data_uri(rid)`
  → `None` for an unknown/corrupt id, then `ref_cat`/`ref_random` are cleared → the paid run proceeds
  unreferenced with no warning. Fix: set `job["warning"]` when `rid` truthy but the uri is `None`.
- **[MEDIUM] `output_delete` refuses FINISHED job dirs** - `:1070-1077`: the active-set collects
  `v["dir"]` regardless of status, so a completed run's folder can't be deleted until eviction. Fix:
  intersect with genuinely-live jobs (`status=="running"` / `thread.is_alive()`).
- **[MEDIUM] Non-atomic libgen resume race** - `libgen_control resume:969-984` runs outside `_REG_LOCK`;
  two resumes both spawn `_run_libjob`. **Corrected framing (r2):** `library_gen._RunLock` (non-blocking
  OS lock) prevents the second run from processing — so **no double-spend** (the r1 "doubled spend" was
  over-stated); the real harm is the loser's `RuntimeError` flipping a live job to `status="error"`.
  Fix: alive-check + thread-swap under `_REG_LOCK`; treat the `_RunLock` RuntimeError as benign.
- **[LOW] `_REG_LOCK` held across disk I/O** in `_evict_finished_lib` (`:912→930`) — snapshot then load
  outside the lock.
- **[LOW] Non-string body fields → `int.strip()` 500** (`bundle_start:779` + token endpoints
  291/304/328/342) — `str(... or "").strip()`. Companion to the r1 `or {}` fix.
- **[LOW] Orphaned job dir on 429** (`libgen_start:909` before the capacity check at `:912-914`) — do the
  capacity check before `prepare_job`, or `rmtree` on the 429 branch.
- **[LOW/PLAUSIBLE] Resume can switch to a costlier model with no re-estimate** (`:980-981`, G19).

## Refuted this round (recorded)
- Double Replicate spend on racing resumes — `_RunLock` prevents the re-run (real impact = error-flip).
- `libgen_control:980` null-body 500 — unreachable (`action=="resume"` needs a dict; null → 400).
- DNS-rebinding / cross-site drive — `_origin_guard` blocks foreign Host + requires local Origin/Referer
  on mutating verbs; money endpoints POST-only. `update_check` allow-list `.evil.com` bypass — fails the
  `startswith("https://nexusmill.com/")` check.
