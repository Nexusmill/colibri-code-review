# Colibri review — asset-forge/forge/imagegen/replicate_flux.py (bug) — ROUND 2

- **source:** `asset-forge/forge/imagegen/replicate_flux.py` (+ byte-identical twin, G23)
- **model:** claude-opus-4-8[1m] lead verification of a primed **claude-opus** scanner (money-critical → deepest tier)
- **sha256 (reviewed, pre-fix):** `ab57fa3485c886d3...` (231 lines)
- **sha256 (post-fix):** `8ff9bd1fa4af7dc72a9493a2595f6957f58461ea2176b957ceac14ba7259a9c7`
- **date:** 2026-07-24 · **mode:** bug · ROUND 2 (DELTA vs r1 `d7dfb395`)
- **context pack:** `get_file_outline`; how `library_gen._run_job_locked` (309-405) drives `generate()`
  — it catches `BilledFailure` and fails the item once, but any OTHER raised exception hits its generic
  `except` and re-calls `generate()` (429 branch or `tries_err<=3`), re-entering the CREATE loop. r1
  fixed the 5xx/timeout create double-bill + the moderation-reject re-bill; RF-2 + LG-1 deferred.

## Verdict
One **genuinely new** money-safety HIGH (post-send connection-reset mis-classified as a safe re-POST →
CREATE double-bill — distinct from the r1 5xx/timeout fix) plus **RF-2 now closed** (poll/download
exhaustion re-bill + partial-file leak). All fixed with pre/post tests (pre 0/4 → post 4/4), twins in
sync. Everything else clean at this depth.

## Findings — Phase-3 dispositions

**[HIGH · FIXED · NEW] `_transient_create` retries a post-send connection reset → CREATE double-bill** — `line 137` (policy) / `154` (trigger) / `159-171` (re-POST)
- **What:** `_transient_create` returned `isinstance(e, ConnectionError)` → `True` for
  `ConnectionResetError`/`ConnectionAbortedError`/`BrokenPipeError`. These are **post-send** drops:
  the create POST sends `Prefer: wait`, the server creates+bills the prediction and holds the socket,
  and a reset during `r.read()` (line 154) means it was already billed. The r1 fix narrowed 5xx/timeout
  but this reset-class was still classified "pure connection failure that never reached the server."
- **Trigger:** a TCP RST while Replicate/an intermediary holds the `Prefer:wait` connection open for a
  slow generation → the loop re-POSTs (up to 3×) → a second/third billed prediction, invisible to
  `library_gen`. CONFIRMED (traced end-to-end; pre-fix test raised raw `ConnectionResetError` after
  re-POSTing). Real-world reset *frequency* is PLAUSIBLE; the misclassification is a certain defect.
- **Fix:** `_transient_create` now retries ONLY provably-pre-send failures (`ConnectionRefusedError`,
  `socket.gaierror` DNS — bare or as a `URLError.reason`); the create raise-block converts the
  reset-class to `BilledFailure` (fail once, never re-POST). VERIFIED: post-fix exactly **1** create
  POST + `BilledFailure`.

**[MEDIUM · FIXED · closes RF-2] poll/download exhaustion re-billed + partial-file leak** — `line 179`, `195`, `_download 217-231`
- The POLL and DOWNLOAD exhaustion `raise`s re-raised the **raw** network error; since the prediction
  is already created+billed, `library_gen`'s generic `except` then retries `generate()` → re-creates +
  re-bills (up to 4× for one image). And `_download` left a truncated `.png` on disk on failure.
- **Fix:** both loops now raise `BilledFailure` (preserving an already-`BilledFailure` cause) so the
  caller fails the item once; `_download` unlinks the partial file in a `try/except`. VERIFIED: poll &
  download exhaustion → `BilledFailure`; partial file removed. **RF-2 → done.**

## Refuted / unchanged (from r1, re-confirmed still valid)
- SSRF via slug/redirect (`_host_ok`+`_NoRedirect`+`_MODEL_RE`), non-standard-port bypass, `extra`
  body-key injection, `_wait` timeout reset, permissive schema fallback, raw `int(seed)` — all remain
  correctly gated / non-triggerable. Not re-charged.

## Still open
- **LG-1** (flux-1.1-pro-ultra priced-but-unmapped) — needs a verified Replicate slug / product
  decision; not addressed here.

## Outcome
- **Money-safety defects fixed:** 2 (new create-reset double-bill HIGH + RF-2 poll/download re-bill &
  partial-file). **Deferred RF-2 → closed.** Twins byte-identical; `sync_builds.py` → *builds in sync*.
- **Not run in a live Flask/Replicate session** — headless-verified (buildenv py3.12).
