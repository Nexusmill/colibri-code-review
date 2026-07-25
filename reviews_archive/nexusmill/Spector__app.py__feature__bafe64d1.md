# FEATURE review: Spector\app.py

- source: `C:\Users\User\source\repos\Nexusmill\Spector\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:34
- tokens: in 2991 / out 1319
- est cost: $0.0288

---

## What this module does
Flask app wrapping a local STL "warehouse" (`Warehouse` class) with a small REST API: ingest/find/delete/reproduce parts, thumbnails, Shape-DNA signatures, backup/export/import packs, and an inbox import — all behind a local-only origin guard.

## Suggested add-ons

**1. Health/readiness + structured request logging** — Value: High · Effort: S
- What: `GET /api/health` returning warehouse root, disk-free space, db reachability, engine availability; plus a `after_request` logger (method, path, status, ms).
- Why: Today failures surface only as raw 500 `{"error": str(e)}` strings with no log trail; a native-window app needs diagnosability when users report "ingest failed".
- How: Add route next to `stats()`; in `_origin_guard`'s module add `import logging, time` and an `@app.after_request` hook writing to `~/.spector/app.log`. Reuse `W.engines_available()` already called in `stats`.

**2. Async job queue for ingest / find / backup** — Value: High · Effort: M
- What: `POST /api/ingest` returns `{"job_id": ...}` immediately; `GET /api/jobs/<id>` polls status/progress.
- Why: Ingest computes Shape-DNA and thumbnails — large STL uploads will block the Flask worker (server is `threaded=True` but the UI still spins on one request) and time out on big files. Batch inbox import (`import_inbox`) especially needs progress.
- How: In-process `concurrent.futures.ThreadPoolExecutor` + dict of job states in `app.py`; endpoints delegate to existing `wh().ingest/find/backup` unchanged.

**3. Batch ingest (multi-file upload)** — Value: High · Effort: S
- What: Accept `request.files.getlist("files")`, loop `_save_upload`/`wh().ingest`, return per-file results/errors.
- Why: Users building a library drag in dozens of STLs; one-file-at-a-time is the top UX friction, and `import_inbox` shows the product already acknowledges bulk workflows.
- How: Extend `ingest()` with a fallback branch when `files` present; reuse the existing try/finally cleanup pattern.

**4. Library filtering / search / pagination on `/api/library`** — Value: High · Effort: S–M
- What: Query params `?q=`, `?tag=`, `?sort=`, `?limit/offset=` passed through to `list_parts()` SQL.
- Why: `list_parts()` returns everything; libraries grow and the current endpoint will degrade and force the frontend to hold full metadata. Tags exist (`rename` accepts them) but can't be queried.
- How: Change `library()` to read `request.args` and forward to a (small) extended `Warehouse.list_parts(filters...)`.

**5. Find-by-part (similarity from existing library item)** — Value: Med · Effort: S
- What: `GET /api/find_similar/<pid>?top=6` — reuse a stored part's DNA instead of requiring a fresh upload.
- Why: `/api/find` only accepts an uploaded file, but the canonical "show me parts like this one" click starts from a library tile whose DNA is already in the db (as `dna_sig` proves).
- How: Fetch the part's stored mesh/DNA via `wh()` and call the same similarity path `wh().find` uses, skipping the temp-file dance.

**6. Consistent error format + error codes** — Value: Med · Effort: S
- What: Central `@app.errorhandler(Exception)` returning `{"error": {"code": "INGEST_FAILED", "message": ...}}`; map known warehouse exceptions to 400 vs 500.
- Why: Currently every handler re-inlines try/except with ad-hoc status codes (delete returns 400, ingest 500); the frontend can't distinguish "bad file" from "server broken".
- How: Replace per-route try/excepts with registered error handlers for a small `WarehouseError` hierarchy.

**7. Backup path sandboxing** — Value: Med · Effort: S
- What: Restrict `POST /api/backup`'s `folder` to an allowlist (e.g. under home dir or configured roots) and reject `..`/system paths.
- Why: The origin guard stops web pages, but any local process can POST an arbitrary absolute path and have the app write a library copy there. `/api/cloud` suggests removable-drive targets, so validate against those.
- How: Validate in `backup()` against `W.cloud_targets()` + `os.path.expanduser("~")` prefix check.

**8. Config surface (port, library root, upload size)** — Value: Med · Effort: S
- What: Env vars `SPECTOR_PORT`, `SPECTOR_MAX_UPLOAD_MB` (`app.config["MAX_CONTENT_LENGTH"]`), log level; `/api/stats` already partially exposes config.
- Why: Port 5005 collides; unbounded uploads can exhaust disk on temp files; users need knobs without editing code.
- How: Read env in the `__main__` block and after `app = Flask(__name__)`.

## Nice-to-haves
- `GET /api/thumb/<pid>` cache headers / ETag — thumbnails are immutable per part.
- `HEAD`/`GET /api/parts/<pid>` metadata endpoint (single-part fetch instead of full library).
- `DELETE` as HTTP DELETE with `/api/parts/<pid>` REST shape (keep alias for compat).
- Upload type sniffing: reject non-STL by magic/extension before `mkstemp` (currently defaults unknown ext to `.stl`).
- Graceful `wh()` failure handling at startup if the library root is unreadable.
- SSE/WebSocket push for inbox count instead of polling `/api/inbox`.
- `top` clamp on `/api/find` (currently unbounded int from form).
- Request ID header for correlating logs once logging (add-on 1) lands.