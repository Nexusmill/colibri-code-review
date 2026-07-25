# Colibri review - Spector/app.py (bug)

- source path: spector/app.py
- reviewer: claude-opus-4-8 (Cowork, colibri G37)
- sha256: ad3e46659782f40d013f2bc405edfe6de97bab755b4b6ecfd602f36e26ecd9b8 (post-fix)
- reviewed sha (pre-fix): 070447db753bc971b26db6dd039a2471f196cf18724e96d3649e28df56241523
- date: 2026-07-24
- mode: bug
- context pack: git log/diff of the 2026-07-24 session (APP-1 async job queue b338f49, APP-2 SSE
  + WH-8 similarity d9203e7); call sites of _job_submit/_events_notify/_save_upload/_quiet_remove;
  _METRICS_LOCK type (threading.Lock), _CHANGES (deque maxlen=512); werkzeug make_server/
  Response.call_on_close verified live (werkzeug 3.1.8). Byte-parity mirror check on asset-forge
  twins (all changed files MATCH). Scope: files changed in today's 12 commits.

## Verdict
Shippable after this tranche. The async job queue's locking, eviction, lazy worker start, and the
202-not-double-counted _log_request gate are sound. Three defects found and fixed, all in the
APP-1/APP-2 additions; worst was a temp-file leak on job cancel.

## Bugs & vulnerabilities (worst first)

**[MEDIUM] Temp-upload leak on cancelled/errored async ingest** - `~line 680`
- What: the async ingest path saves every upload with tempfile.mkstemp BEFORE submitting the job;
  each temp file is removed only inside its own step's `finally`. The worker checks
  `if job["cancel"]: break` BEFORE calling the step, so cancel (POST /api/jobs/<id>/cancel, a
  supported action) or any step contract-break leaves un-run steps' temp files on disk forever.
- Trigger: submit N files with ?async=1, cancel before all steps run. Confirmed end-to-end.
- Impact: up to _ASYNC_BATCH_MAX (500) leaked temp files per cancelled job; accumulates until OS
  temp cleanup.
- Fix: register a `finalize` on the ingest job that _quiet_remove()s every saved path; finalize
  runs on EVERY worker exit path and _quiet_remove is idempotent. Verified: 5-step job cancelled
  before run -> 0 steps run, 0 files leaked (was 5).

**[LOW] SSE lost-wakeup race** - `_events()` generator
- What: predicate (_CHANGES/_LIB_VERSION) checked under _METRICS_LOCK but the wait used a separate
  bare _EVT_COND. A bump+notify landing between the check and _EVT_COND.wait() was lost.
- Impact: that change delivered up to _SSE_KEEPALIVE_S (15s) late; not data loss.
- Fix: _EVT_COND = threading.Condition(_METRICS_LOCK); predicate check + wait now share one lock.
  Both _events_notify call sites notify outside the lock (no re-entrancy). Verified: waiter woken
  in 0.000s; no deadlock.

**[LOW] SSE client-slot leak if the stream generator is never iterated** - `_events()`
- What: _SSE_CLIENTS incremented in the view, decremented only in the generator finally; an
  un-started generator never freed the slot, eventually 503-ing all new streams.
- Fix: decrement via resp.call_on_close(_release) (Werkzeug closes the response even when the body
  is never iterated); dropped the generator finally. Cap still enforced atomically in the view.

## Missing safeguards
- similarity_pct(eps=0) returns nan rather than None (warehouse.py) - only reachable via misconfig;
  left as-is (out of this tranche).

## Clean in this session (traced, no findings)
warehouse.py (WH-2/6/8/9 - RLock, blobs dir precedes startup GC, numpy chamfer numerically
identical to scipy), launcher.py (make_server bind-and-hold; server_port verified; HTTPError-
before-OSError ordering correct), prompts.py + app.py styles + library_gen.py (save_settings
merges - no data-loss), PatternSkin __init__.py PSK-7 (vgroup falloff equivalent) and
part_export.py PE-1 (uniquifier). Separate LOW note: PSK-7 fast branch subscripts me.vertices
with a numpy int where the old code used int() - almost certainly fine (np ints implement
__index__), unverified without live Blender.
