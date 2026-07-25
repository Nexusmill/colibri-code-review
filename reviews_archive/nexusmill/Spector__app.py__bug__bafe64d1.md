# BUG review: Spector\app.py

- source: `C:\Users\User\source\repos\Nexusmill\Spector\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:33
- tokens: in 3034 / out 2411
- est cost: $0.0453

---

## Verdict
Not quite safe to ship as-is. The single biggest risk is that the CSRF/origin guard on line 41-44 allows state-changing POSTs (ingest, delete, backup, import) when the `Origin` and `Referer` headers are simply absent, which is trivially achievable for cross-site requests that strip referrers — defeating the guard the file's own docstring says protects filesystem writes.

## Bugs & vulnerabilities

**[HIGH] Origin guard passes POSTs with no Origin/Referer headers** - `lines 36-44`
- What: Every check is conditional: `if origin and ...`, `if ref and ...`. A cross-site request that suppresses both headers (e.g., a page with `<meta name="referrer" content="never">` plus a browser that omits `Origin` on same-origin-ambiguous form posts, or any non-browser client a malicious page can induce via `fetch` with `mode: 'no-cors'` form-style POSTs on browsers without `Sec-Fetch-Site` support — Safari, older Firefox) sails through and can hit `/api/delete/<pid>`, `/api/backup`, `/api/import`.
- Trigger: Cross-site POST with `Sec-Fetch-Site` unsupported/absent and no `Origin`/`Referer`.
- Impact: Attacker web page drives destructive/write APIs (delete library parts, ingest junk, write backups to arbitrary folders) despite the guard's stated purpose.
- Fix: For non-GET methods, *require* a local Origin or Referer: reject when both headers are absent, e.g. `if request.method not in SAFE and not (origin or ref): return 403`. `Sec-Fetch-Site` alone is not universal.

**[MEDIUM] `/api/export` leaks temp file and returns unhandled 500 on failure** - `line 168`
- What: Unlike every other endpoint, there is no try/except around `wh().export_pack(p)`. If it raises (disk full, DB locked, corrupt part), the `mkstemp` file `p` is never removed, and Flask returns an HTML 500.
- Trigger: Any exception inside `export_pack`.
- Impact: Temp-file litter accumulates per failed export; inconsistent error contract vs. other endpoints.
- Fix: Wrap in try/except mirroring `reproduce()` (lines 132-137): remove `p` and return `jsonify({"error": ...}), 500`.

**[MEDIUM] Shared `Warehouse`/SQLite handle across `threaded=True` requests** - `lines 13-21, 213`
- What: `_WH` is a module-global singleton initialized lazily, and the server runs `threaded=True`. If `warehouse.Warehouse` holds a single `sqlite3.Connection` (as line 79's `wh().db.execute` suggests), concurrent requests will hit `sqlite3.ProgrammingError: objects created in a thread can only be used in that same thread`, or race during lazy init (two threads both construct `Warehouse`, one is orphaned/leaked).
- Trigger: Two simultaneous requests on a fresh server (init race), or any concurrent DB access.
- Impact: Intermittent 500s under normal multi-tab UI use; leaked connection/handles from double init.
- Fix: Use a lock around lazy init, and make DB access per-thread (Flask `g`) or confirm `Warehouse` uses `check_same_thread=False` plus internal locking — and document it.

**[LOW] `int(request.form.get("top", 6))` unvalidated** - `line 121`
- What: Non-integer `top` raises `ValueError` (caught, but reported as a 500 "server error" instead of a 400 client error); huge values (e.g. `top=10**9`) are passed straight to `wh().find` with no upper bound.
- Trigger: `top=abc` or `top=1000000000`.
- Impact: Misleading error classification; potential resource exhaustion in similarity search.
- Fix: Parse inside a try and return 400 on failure; clamp to a sane range (e.g. `1 <= top <= 100`).

**[LOW] `/api/rename/<pid>` has no error handling and silently accepts a no-op** - `lines 200-209`
- What: `wh().rename(pid, name, tags)` is not wrapped; an unknown `pid` or DB error yields an unhandled HTML 500, unlike sibling endpoints. Also, when both `name` and `tags` are `None` the endpoint reports `{"ok": True}` while doing nothing (or clobbering, depending on `Warehouse.rename` semantics with `None`).
- Trigger: POST rename for a deleted/nonexistent pid, or `{}` body.
- Impact: Inconsistent error surface; possible silent no-op or unintended nulling of fields.
- Fix: Wrap in try/except → 400/404; reject bodies where both fields are absent.

**[LOW] `np.frombuffer` on corrupt `dna` blob raises unhandled** - `line 82`
- What: If the stored BLOB length isn't a multiple of 8 bytes (corruption, older schema), `np.frombuffer(..., np.float64)` raises `ValueError` → HTML 500. All other endpoints JSON-wrap errors.
- Trigger: Corrupt/legacy `parts.dna` row.
- Impact: 500 with HTML body on a GET tile-barcode request.
- Fix: Wrap in try/except and return `{"sig": []}` on malformed data.

**[LOW] Upload suffix derived from attacker-controlled filename** - `line 55`
- What: `ext = os.path.splitext(f.filename or "")[1]` is passed directly as `mkstemp(suffix=ext)`. A filename like `x/../../y` yields an ext containing no separators in practice (splitext stops at the last dot), but an ext containing os separators or absurd length will make `mkstemp` raise — and here the failure happens *before* `p` exists, so it's just a 500, but with no error JSON (ingest does wrap it; fine) — the real issue is there's no allowlist, so the temp file can carry an executable-looking suffix (`.bat`, `.exe`). Local-only, but the file is later handed to parsers by extension.
- Trigger: Upload with filename `part.exe`.
- Impact: Temp file written with attacker-chosen extension; downstream sniffing by extension may misparse.
- Fix: Validate ext against the supported model formats (e.g. `.stl`, `.obj`, `.3mf`, `.step`), default to `.stl`.

## Missing safeguards
- `Sec-Fetch-Site` values `same-site`/`none` are accepted unchecked — combined with the absent-Origin hole, CSRF defense needs a mandatory-Origin rule for mutating verbs (see HIGH finding).
- No request size limit (`app.config['MAX_CONTENT_LENGTH']`): uploads to `/api/ingest`, `/api/find`, `/api/import` are unbounded → memory/disk DoS on the local machine.
- `backup(folder)` takes an arbitrary absolute path with no validation/sandboxing — even for a local app, confirm `Warehouse.backup` can't be abused (e.g., writing into `~/.ssh`) given the CSRF gap above.
- No test coverage for: guard rejection paths (foreign Host, missing Origin on POST), export failure cleanup, rename of nonexistent pid, corrupt `dna` blob, and concurrent first-hit init of `wh()`.
- `/api/cloud`, `/api/import_inbox`, `/api/inbox` delegate blindly; if `cloud_targets`/`import_inbox` touch the network, the "nothing leaves the machine" claim in the module docstring needs enforcement/tests.
- Error responses echo raw exception strings (`str(e)`) everywhere — low risk locally, but it leaks filesystem paths into API responses; consider a generic message with server-side logging.