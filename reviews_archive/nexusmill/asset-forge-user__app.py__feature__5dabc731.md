# FEATURE review: asset-forge-user\app.py

- source: `C:\Users\User\source\repos\Nexusmill\asset-forge-user\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:32
- tokens: in 11445 / out 1634
- est cost: $0.0588

---

## What this module does
A local-only Flask web app ("Asset Forge") that generates pattern texture sets (procedural and AI-image bundles via Replicate), stamps them with buyer personalization and cryptographic tracers, manages a user library, and serves downloads/zips — with a hardened same-origin security guard and self-service error diagnostics.

## Suggested add-ons

**Bundle job cancellation + pause/resume parity**  -  Value: High · Effort: S
- What: Add a `/api/bundle/control/<job_id>` endpoint with cancel (and pause if the provider supports it), matching what `library_gen` jobs already have.
- Why: AI bundle jobs spend real Replicate credits; a user who mistypes a theme or count currently has no way to stop the spend — the biggest UX gap given `/api/library_gen/control` already proves the pattern works.
- How: In `bundle_start`, store a `control` dict in `_JOBS[job_id]`; thread it into `_bundle.build_bundle` (or check it in the `prog` callback in `_run_bundle` and raise a `Cancelled` exception the existing `except` turns into a clean status). Reuse the `libgen_control` handler shape.

**Cost estimation before bundle start**  -  Value: High · Effort: S
- What: Return/display estimated cost per bundle run before the user clicks Generate.
- Why: `library_gen/estimate` already exists and reports `spent_est`; bundle runs are equally credit-consuming but blind. Prevents buyer sticker-shock support tickets.
- How: Factor `_libgen.estimate`'s per-model pricing into a shared helper; call it from `bundle_start` (or a new `/api/bundle/estimate`) using `model` + `count`, and surface it in the front end.

**Persistent job history / resume for bundle jobs**  -  Value: High · Effort: M
- What: Write bundle job state to disk (like `_libgen._write_job` / `load_job`) so a restart doesn't orphan running jobs and users can re-download past bundles.
- Why: `_JOBS` is in-memory; killing the app mid-run loses progress with money already spent, and there's no "my past sets" listing despite `output/` holding everything.
- How: Mirror the `_libgen` job-file pattern: write `BUNDLE_*.job.json` in `out_dir` from `_run_bundle`, add `/api/bundle/history` scanning `OUTPUT / "bundle_*"`, and offer resume on startup.

**Output folder management (list + delete + disk usage)**  -  Value: High · Effort: S
- What: Endpoints to list `OUTPUT` subfolders/zips with sizes and delete chosen ones.
- Why: Every generate/preview/bundle run leaves a folder AND a zip forever; on a local asset tool this silently eats gigabytes. Users currently must hand-clean `output/`.
- How: `_safe_under_output` already guards traversal — add `/api/output/list` (name, size, mtime, kind) and `/api/output/delete` (dir-only, refuse library dir). Show total disk use in settings.

**Batch verify**  -  Value: Med · Effort: S
- What: Let `/api/verify` accept multiple files (or a zip) and return per-file verdicts.
- Why: Verifying a leaked asset one file at a time is tedious; a marketplace seller checking a suspicious pack wants bulk CLEAN/FORGED/VERIFIED results.
- How: `request.files.getlist("file")`, loop the existing extract/identify logic, return a list of the same payload dicts. The temp-file handling in `verify` is already per-file safe.

**Request/job logging with rotation**  -  Value: Med · Effort: S
- What: Structured app log (generation params minus secrets, job lifecycle, durations) alongside the error reports.
- Why: Only failures leave a trail today; "it made the wrong thing" or "I was charged twice" reports have nothing to corroborate. `_redact` is already there to keep logs safe.
- How: `logging.handlers.RotatingFileHandler` to `OUTPUT/logs/app.log`; log in `generate`, `_run_bundle` prog callback, `_run_libjob`, and token save/validate (redacted).

**Groq token onboarding parity**  -  Value: Med · Effort: S
- What: Validate/save endpoints for `GROQ_API_KEY` mirroring the Replicate token flow.
- Why: `/api/token/status` and `/api/options` advertise `groq_ready`, but there's no way to set the key from the UI — users must hand-edit `providers.env`.
- How: Copy `token_validate`/`token_save` with a Groq `/models` ping; call `_cfg.save_provider("GROQ_API_KEY", ...)`.

**Provider retry/backoff for transient Replicate failures**  -  Value: Med · Effort: M
- What: Automatic retry with backoff on 429/5xx/network errors during bundle and library-gen image calls.
- Why: One flaky request currently fails a whole multi-image job (and partial spend). Rate limits are routine on Replicate.
- How: Wrap the prediction call inside `_bundle.ReplicateProvider` (single hook point used by both `_run_bundle` and `_run_libjob`); expose `max_retries` in settings. Surface "retrying…" via the `prog`/`log` channel.

**Per-file preview/re-serve without download headers**  -  Value: Med · Effort: S
- What: An inline (non-attachment) variant of `/api/asset/<path>` so the UI can lightbox full-size images.
- Why: Only 160–320px thumbnails are viewable (`userlib_thumb`, `_thumb_b64`); inspecting a full-res texture forces a download-and-open round trip.
- How: Add `?inline=1` to `asset_file` → `send_file(p, as_attachment=False)` with correct mimetype; traversal guard already in place.

## Nice-to-haves
- **Graceful job eviction notice**: `_JOBS.pop(next(iter(_JOBS)))` silently drops jobs; mark evicted entries or persist before dropping so polling a dropped job returns "expired" instead of 404.
- **`/api/health` endpoint** exposing `_diagnostics()` (already built) for the front end's status bar.
- **Cache thumbnails on disk** (`userlib_thumb`/`lib_thumb` regenerate base64 PNGs on every request; content-hash-named cache files would help large libraries).
- **Configurable host/port** via env (`AF_PORT`) instead of hardcoded 5000 — port conflicts are a classic support issue.
- **Zip streaming**: `zipfile` builds whole zips in `OUTPUT` before download; for big bundles, stream with `zipstream`-style generation to avoid double disk usage.
- **Duplicate `_personalize.stamp_dir` guard**: `generate` stamps after `_publish_to_library` (correct), but `_zip_dir` stamps again at zip time — an idempotence check (marker file) would prevent accidental re-stamping drift.
- **Manifest index**: `verify` does a recursive glob over all manifests per lookup; a tiny JSON/SQLite index of `set_id → manifest path` built at generate time makes verify O(1).
- **Settings validation**: `settings_set` accepts any `library_dir` string without checking writability — validate with a probe write and return a friendly error.
- **Rate-limit update_check**: cache the `version.json` result for N hours to avoid hitting nexusmill.com on every page load.