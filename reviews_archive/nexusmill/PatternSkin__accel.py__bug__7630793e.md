# colibri gate — PatternSkin/accel.py (grok round 6, delta)

- **source:** PatternSkin/accel.py
- **model:** grok-4.3 (external, .grok_reviews/2026-08-22_accel_grok43.md) gated in-session by claude-fable-5
- **sha256:** 7630793eb08788ea... (current bytes at dispatch, G36) — DELTA vs the r3 review (sha bf42721d, closed); file drifted via our own r3 remediation
- **date:** 2026-08-22 · **mode:** bug (grok round 6, delta)
- **context pack:** cupy→torch ladder ruling + ACCEL-1 3 LOWs + closed r3/float32/warmup items pre-declared; verified against get_xp, _WorkerClient._spawn/request, _worker_lock.

## Verdict
One NEW keeper (a latent worker-spawn deadlock hazard), and one re-report of an
already-deferred item. Delta discipline held — no re-litigation of r3.

## Findings after adversarial verification

**[HIGH hazard, PLAUSIBLE on trigger frequency — NEW] `_WorkerClient._spawn` leaves stderr=PIPE undrained with a blocking stdout read, inside `_worker_lock()`** — accel.py:1163-1180
- Verified code: `subprocess.Popen([...], stdout=PIPE, stderr=PIPE, text=True)` then `port_line = self.proc.stdout.readline()` (blocking, NO timeout) then `int(port_line.strip())`. Called at request():1195 inside `with _worker_lock():` + a try/except.
- Two failure modes traced:
  1. **Hang (the load-bearing risk):** the parent NEVER reads the worker's stderr. The worker is persistent ("for the whole session"). If it writes more than the OS pipe buffer (~64 KB) to stderr — at import (torch/cupy CUDA/driver warnings) or accumulated over the session — it blocks on its next stderr write, and any parent `stdout.readline()`/spawn wedges forever. A hang is NOT caught by request()'s try/except and it holds `_worker_lock()`, so it wedges the ENTIRE worker subsystem, not one request. **PLAUSIBLE because** whether the worker actually emits >64 KB to stderr needs runtime observation I can't do from text — but the undrained-PIPE + blocking-read + no-timeout + held-lock pattern is a textbook latent deadlock and warrants the fix regardless.
  2. **Empty-port ValueError (CONFIRMED but contained):** if the worker dies at import before printing a port, `readline()` returns `''` → `int(''.strip())` → ValueError. This one IS contained — _spawn runs under request()'s try/except → failure count → CPU fallback (self-heals). Not the concern; the hang is.
- Fix (Grok's, sound): `stderr=subprocess.DEVNULL` (the parent never reads it anyway — cleanest), and a timeout/`select` on the first-line read (or guard the empty/non-int port line) so a silent worker can't block the lock. The experimental separate-process GPU tiers are opt-in, which bounds how often this is reachable, but a session-wedging hang is worth closing.

**[MEDIUM — NOT NEW, matches deferred ACCEL-1 #3] get_xp CPU-fallback doesn't invalidate caps, so active_tier_key/best_tier/tech_status misreport the GPU tier** — get_xp:1002-1013
- Verified: on the cupy/torch import `except`, get_xp logs `_log_event(...)` and returns numpy WITHOUT `_invalidate_caps()`, so `capabilities()` still reports cupy/torch True and the tier reporters keep naming the GPU tier while work runs on numpy. Real path.
- **This is the already-docketed ACCEL-1 #3** (deferred 2026-07-24: "gpu_healthy() discards get_xp()'s tag ... active_tier_key keeps reporting the GPU tier while work runs on CPU. Narrow."). Pre-declared in the context pack; recorded here as matching an OPEN deferred docket, NOT a new finding, NOT re-fixed (delta/G35 discipline). Grok's refinement — invalidate inside get_xp's/sample_tiled_xp's except rather than only in gpu_healthy — is a useful implementation note to attach to ACCEL-1 when Damien takes that docket, but it does not change the finding's status.

## Refuted / not-new
- The cupy→torch ladder is NOT flagged (standing Damien ruling, pre-declared).
- The active_tier_key MEDIUM is folded into ACCEL-1 #3, not opened as new.
