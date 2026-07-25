# Colibri review — PatternSkin/replicate_client.py (bug) — ROUND 2

- **source:** `PatternSkin/replicate_client.py` (vendored paid Replicate client; NOT a twin — the
  asset-forge sibling is the separate `forge/imagegen/replicate_flux.py`)
- **model:** claude-opus-4-8[1m] (in-session; cross-file lead from the replicate_flux r2 finding)
- **sha256 (reviewed, pre-fix):** `43c9db799027bb229582719cf8dae78a1c261928d33878c740152232ed2e2387`
- **sha256 (post-fix):** `c3ed9817fa2a88ef...`
- **date:** 2026-07-24 · **mode:** bug · ROUND 2 (DELTA vs r1 `f143644d`)
- **context pack:** r1 review (fixed the 5xx/timeout create double-bill; RC-1 deferred). Cross-file:
  the **replicate_flux.py r2 fix** (commit c9c764b) just found the post-send connection-reset
  double-bill class — this file is the sibling client with the same retry shape, so the colibri
  "duplication of logic across the repo" check flagged it directly. Sole caller: `filmstrip.py`
  (daemon thread, broad `except Exception`). Pure stdlib → headlessly testable.

## Verdict
The sibling of the flux double-bill class is present and **worse-placed**: the create `URLError`
branch retried on ANY non-timeout `URLError`, so a `URLError` wrapping a post-send
`ConnectionResetError` (a drop during the `Prefer:wait` response-header wait, where the prediction is
created+billed) was **re-POSTed up to 5×** = 5 billed predictions. Fixed + verified (pre 1/3 → post
3/3). Two related robustness fixes bundled.

## Findings — Phase-3 dispositions

**[HIGH · FIXED] post-send connection reset on CREATE → up to 5 billed predictions** — `line 140-148`
- **What:** the `URLError` branch retried `if not _timed_out and attempt < 4`. `_timed_out` was true
  only for `socket.timeout`/`TimeoutError`, so a `URLError(reason=ConnectionResetError/Aborted/
  BrokenPipe)` — a drop after the request was sent, during the `Prefer:wait` header wait where the
  prediction is already created+billed — fell through as "retryable" and re-POSTed (5 attempts).
- **Phase-3:** CONFIRMED — pre-fix test issued **5** create POSTs on a `URLError(ConnectionReset)`.
- **Fix:** retry ONLY provably-pre-send failures (`ConnectionRefusedError`, `socket.gaierror` DNS);
  read-timeout + reset-class → a "may have been created and billed" `RuntimeError`, never re-POST.
  VERIFIED: post-fix **1** POST + billing warning; connection-refused still retries (5, unchanged).

**[MEDIUM · FIXED] bare `ConnectionResetError` from `r.read()` was uncaught** — `line 120`
- The create try caught only `HTTPError`/`URLError`/`ValueError`; a reset while reading the body of an
  already-created (200) prediction raised a bare `ConnectionResetError` that escaped the client's
  `RuntimeError` contract to the caller. CONFIRMED (pre-fix leaked it). **Fix:** `except OSError` →
  a "created and billed" `RuntimeError` (post-headers = billed; do not retry).

**[LOW · FIXED] output download left a truncated file on failure** — `line 178-187`
- `open(out_path,"wb")` then a mid-stream failure left a partial `.png`. **Fix:** `try/except` unlinks
  the partial file on any error (mirrors the flux `_download` fix).

## Still open
- **RC-1** (deferred): fold the create-retry phase into the single `timeout` clock **and** add a
  `cancel()`/`DELETE` helper so an abandoned run can release still-billing predictions. Unchanged by
  this fix (this closed the re-POST double-bill; RC-1 is the cancel-helper feature). Stays deferred.

## Outcome
- **Money-safety defects fixed:** 1 HIGH (create-reset double-bill) + 2 supporting (uncaught read-reset,
  partial-file leak). Single file (no twin). VERIFIED `junk/_rc_r2_test.py` pre 1/3 → post 3/3
  (`_rc_urlopen` monkeypatched, no network). NOT run in a live Blender session (headless-verified).
