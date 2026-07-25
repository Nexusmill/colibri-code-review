# BUG review: asset-forge\app.py

- source: `C:\Users\User\source\repos\Nexusmill\asset-forge\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 20:47
- tokens: in 15718 / out 5182
- est cost: $0.1249

---

## Verdict
Not quite safe to ship: the origin/host guard and path-traversal handling are solid, but generation endpoints accept unbounded counts and several JSON fields crash or misbehave on `null`, and library publishing silently overwrites same-named files. The single biggest risk is unauthenticated local callers (or a single malicious/buggy client) filling the disk or burning API spend via unbounded `count` in `/api/generate`, `/api/bundle/start`, and `/api/library_gen/start`.

## Bugs & vulnerabilities

**[MEDIUM] Unbounded `count` allows disk-exhaustion / unbounded spend** - `lines 418, 677, 722`
- What: `int(d.get("count", 6))` / `int(params.get("count", 8))` are passed straight to the pipeline/provider with no upper bound or even type check.
- Trigger: `POST /api/generate {"category":"x","family":"y","seed":1,"count":10000000}` or a bundle start with a huge count.
- Impact: `pipeline.generate_set` writes unlimited files into `OUTPUT` (disk fill DoS); bundle/library jobs burn Replicate credits at scale. `/api/bundle/estimate` caps count at `max(1, ...)` but the actual start endpoints never validate it.
- Fix: clamp/validate at the boundary, e.g. `count = max(1, min(int(...), 256))` and return 400 on non-integer, in `generate`, `bundle_start`, and `_libgen.build_plan` input.

**[MEDIUM] `_publish_to_library` silently overwrites existing library files** - `line 62`
- What: `(dst / f.name).write_bytes(f.read_bytes())` overwrites, while `library_file` (line 545) deliberately *keeps* existing files. Two sets in the same category/family that emit the same filename (e.g. `brick_01.png` from different seeds) clobber the earlier library asset. Per-file `except Exception: pass` (line 63) also hides all write failures.
- Trigger: generate two sets with the same family naming scheme.
- Impact: silent, unrecoverable loss of previously generated/published library textures; inconsistent with the documented "merge, keep existing" semantics.
- Fix: skip when `(dst / f.name).exists()` (matching `library_file`), or de-duplicate the name; at minimum log failed copies instead of bare `pass`.

**[MEDIUM] `output_delete` races running jobs and can delete their live output dirs** - `lines 987-1003`
- What: deletion only checks the path is under OUTPUT and not named `library`/`error_reports`; it never checks `_JOBS`/`_LIBJOBS` for an active job writing into that directory.
- Trigger: start a bundle job, then `POST /api/output/delete {"names":["bundle_<slug>_<stamp>_<jobid>"]}` while it runs.
- Impact: paid generation writes into a deleted tree; `_snapshot_bundle_job` and `_zip_dir` then fail or produce partial/corrupt zips; job state and money are lost silently.
- Fix: refuse deletion of any dir referenced by a running entry in `_JOBS` / `_LIBJOBS`.

**[MEDIUM] `.strip()` / `.get()` on explicit JSON `null` crashes multiple endpoints** - `lines 268, 281, 305, 317, 416, 831`
- What: `.get("token", "")` / `d.get("buyer_name", "")` return `None` when the client sends `{"token": null}` — the default only applies to a *missing* key. `None.strip()` raises; line 831 does `params.get("selection", {}).get("packs")` which crashes on `{"selection": null}`.
- Trigger: `POST /api/token/validate {"token": null}`; `POST /api/generate {"sale":true,"buyer_name":null,...}`; `POST /api/library_gen/start {"selection": null}`.
- Impact: unhandled 500s that each write an error report to disk and return a traceback-flavored payload — noisy, and in `generate` can abort mid-flow after work has started.
- Fix: normalize with `str(d.get("token") or "").strip()` and `(params.get("selection") or {})`.

**[LOW] Temp file leak in `_verify_one` when the write fails** - `lines 450-457`
- What: `tmp.write_bytes(data)` sits *outside* the `try/finally` that unlinks the temp file.
- Trigger: disk full / permission error during `write_bytes`.
- Impact: orphaned temp files accumulate on repeated failures.
- Fix: move `write_bytes` inside the `try`, or wrap create+write+extract in one `try/finally`.

**[LOW] Thumbnail endpoints 500 on malformed data URIs** - `lines 575, 584`
- What: `base64.b64decode(uri.split(",", 1)[1])` — if `_userlib.thumb_uri` / `_lib.thumb_uri` ever returns a truthy string without a comma, the `[1]` index raises `IndexError`; invalid base64 also raises.
- Trigger: any future/refactored `thumb_uri` returning a plain path or empty-ish string.
- Impact: 500 instead of 404.
- Fix: `if "," not in uri: return ("no image", 404)` and wrap `b64decode` in try/except.

**[LOW] Job-cap check is a TOCTOU race under `threaded=True`** - `lines 719-724, 842-847`
- What: `_evict_finished` returns "room for one more," then the job is inserted — but two concurrent `/api/bundle/start` requests can both pass the check before either inserts.
- Trigger: simultaneous double-click / parallel requests.
- Impact: registry exceeds `MAX_TRACKED_JOBS`; mostly benign but defeats the bound.
- Fix: guard check-and-insert with a `threading.Lock` around `_JOBS`/`_LIBJOBS`.

**[LOW] `zip_selected` can overwrite an existing set's zip** - `lines 1016-1018`
- What: `zp = OUTPUT / zname` opens with `"w"`; a client-supplied `zipname` matching an existing set's zip name truncates it before writing the subset.
- Trigger: `POST /api/zip_selected {"dir":"sale_x_...","names":["a.png"],"zipname":"sale_x_..."}`.
- Impact: destroys the original full-set zip (data loss, though the dir still exists).
- Fix: refuse if `zp.exists()`, or suffix a uuid like `generate` does (line 412).

**[LOW] Orphaned library-gen job dirs on 429** - `lines 839-843`
- What: `_libgen.prepare_job(_lib_out(), params)` creates the on-disk job dir *before* `_evict_finished_lib` can reject the request; on 429 the prepared dir is left behind untracked.
- Trigger: exceed `MAX_TRACKED_JOBS` active library jobs, then start another.
- Impact: littered half-initialized job folders in the user's library dir with no UI path to resume them.
- Fix: run the eviction check before `prepare_job`.

**[LOW] Unredacted exception text in the `"error"` field of error payloads** - `lines 205, 220, 704`
- What: the *report* is run through `_redact`, but `"error": str(exc)` is returned raw. Provider/library exceptions can embed URLs or env-derived paths containing credentials (e.g. a malformed `providers.env` value echoed by a config error).
- Trigger: any exception whose message contains a token-shaped string.
- Impact: secret material returned to the client and stored in job state served by `/api/bundle/poll`.
- Fix: use `_redact(str(exc))` in `_error_payload` and line 704.

## Missing safeguards
- No upper-bound/type validation on `count`, `seed`, `ref_strength` (line 664: `float(None)` crashes on explicit null) at any generation entry point.
- `/api/verify` batch has no cap on number of files per request (only total body size); each file up to 50MB is decoded sequentially — fine for memory, but a 100MB batch of SVGs runs XML parsing with no documented bomb protection in `extract_svg`.
- No locking anywhere around `_JOBS`/`_LIBJOBS` mutation vs. polling; dict ops are GIL-atomic but multi-step sequences (evict-then-insert, control-dict mutation at lines 746, 899-905) are not.
- `library_types` (line 511) walks the entire user-configurable library dir on every request with no depth/size limit — a library dir pointed at a huge tree makes this endpoint hang.
- No tests evident for the null-JSON-body paths, the `_safe_under_output` edge cases (empty relpath resolves to OUTPUT itself and passes the check at line 917), or concurrent start/delete races.
- `model_schema` passes a raw user-supplied model slug into `_caps` (line 386) which likely builds a Replicate API URL — no allowlist against `_MODELS` keys, so arbitrary path segments reach the provider client.