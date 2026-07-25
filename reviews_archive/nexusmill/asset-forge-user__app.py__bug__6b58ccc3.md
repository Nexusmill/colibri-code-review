# BUG review: asset-forge-user\app.py

- source: `C:\Users\User\source\repos\Nexusmill\asset-forge-user\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 20:50
- tokens: in 15719 / out 4420
- est cost: $0.1135

---

## Verdict
Mostly shippable for a local-only app — the origin guard, traversal helper, and size caps are genuinely thoughtful — but it leaks/clobbers files in a few edge paths and has no cap on generation counts. Biggest single risk: `/api/generate` (and friends) accept an unbounded `count`, letting one small request exhaust disk/CPU, and the delete-guard in `output_delete` can be bypassed when the app is launched from a relative path.

## Bugs & vulnerabilities

**[MEDIUM] Unbounded `count` / `seed` — disk & CPU exhaustion via tiny JSON** - `lines 417-420` (also `bundle_start` 722, `_run_bundle` 677)
- What: `int(d.get("count", 6))` is passed straight to `pipeline.generate_set` with no upper bound; `MAX_CONTENT_LENGTH` only caps the *request body*, not the work it schedules. A 60-byte JSON `{"count": 100000000}` starts a run that writes textures until the disk fills. Same for `bundle count` (which also spends Replicate credits — `bundle_estimate` clamps with `max(1, ...)` but `bundle_start`/`_run_bundle` do not clamp at all, so `count=0` or negative also produces a nonsensical run).
- Trigger: `POST /api/generate` with a huge or zero/negative `count` (also a broken/malicious local page that passes the origin guard, or a buggy client).
- Impact: unbounded disk consumption under `output/`; for bundles, unbounded paid API spend.
- Fix: clamp centrally, e.g. `count = min(64, max(1, int(d.get("count", 6))))` with a 400 on non-integer, in `generate`, `bundle_start`, and `_run_bundle`.

**[MEDIUM] `output_delete` guard compares resolved path against unresolved `OUTPUT`** - `line 989`
- What: `_safe_under_output` returns `(OUTPUT / n).resolve()` (line 916), but the refusal check is `p == OUTPUT` where `OUTPUT = BASE / "output"` and `BASE = Path(__file__).parent` (lines 25-26). If the app is launched so that `__file__` is relative (e.g. `python app.py` from some directories/packagers), `OUTPUT` is a relative path and `p == OUTPUT` is never true for the resolved `p` — the "don't delete the root" check is dead. `{"names": ["."]}` or `""` then resolves to the OUTPUT root and `shutil.rmtree(p)` deletes *everything*, including `library/` and `error_reports/` (the per-name refusal only fires when the entry itself is named "library").
- Trigger: relative `__file__` + `POST /api/output/delete {"names": ["."]}`.
- Impact: deletion of the entire output tree including the user's merged library and error reports.
- Fix: resolve once: `OUTPUT = (BASE / "output").resolve()` at module load, and compare `p == OUTPUT.resolve()`; also explicitly refuse the OUTPUT root inside the delete loop regardless of name.

**[MEDIUM] Temp file leak in `_verify_one` on write failure** - `lines 450-457`
- What: `tmp.write_bytes(data)` sits *outside* the `try/finally` that unlinks the temp file. If `write_bytes` raises (disk full, perms), the `mkstemp` file in the system temp dir is never removed; the `finally` only covers `extract_png`.
- Trigger: disk-full or temp-dir error during a verify upload.
- Impact: orphaned files accumulate in `/tmp` per failed verify.
- Fix: wrap from immediately after `mkstemp`: `try: tmp.write_bytes(data); token, src = extract_png(...) finally: tmp.unlink(missing_ok=True)`.

**[MEDIUM] Evicted library jobs become permanently unresumable** - `lines 851-859`, `862-866`, `881-909`
- What: `_evict_finished_lib` pops entries whose thread is dead — including *paused* jobs (a paused job's worker exits between images, so `thread.is_alive()` is False). Once evicted (after 32 jobs), `libgen_poll`/`libgen_control` 404 because they only consult `_LIBJOBS`, and there is no endpoint that re-attaches to the on-disk job file by directory. The on-disk job state still says "paused", but the UI can never resume it.
- Trigger: pause a library job, run ~32 more jobs, try to resume the first.
- Impact: paid, partially-completed library runs silently lose their resume path (the exact "money already spent" failure mode `_snapshot_bundle_job` was built to prevent for bundles).
- Fix: on `poll`/`control` 404, fall back to locating the job file on disk (e.g. by `job_id` glob under the library dir) and re-register the entry, or persist an index of job_id → dir.

**[LOW] `zip_selected` lets a client clobber any existing zip in OUTPUT** - `lines 1016-1018`
- What: `zname` is derived from user-supplied `zipname` and opened with `"w"` with no collision check. Separators are stripped so traversal out of OUTPUT isn't possible, but `zipname="sale_set_20240101_120000_ab12cd"` (or any existing zip's name) silently overwrites that archive.
- Trigger: `POST /api/zip_selected` with `zipname` equal to an existing zip's basename.
- Impact: destruction of a previously generated/downloadable archive (data loss, no error).
- Fix: refuse if `zp.exists()` or suffix a uuid, mirroring the collision fix already applied in `generate` (line 412 comment).

**[LOW] Job registries mutated without a lock; check-then-insert race in `_evict_finished*` ** - `lines 612-619, 719-724, 842-847`
- What: `_evict_finished(_JOBS)` (returns "room for one more") and the subsequent `_JOBS[job_id] = ...` are not atomic; two concurrent `bundle_start` requests can both see room and push the registry past `MAX_TRACKED_JOBS`, and dict iteration in `bundle_poll`/eviction races with mutation from worker threads (`job.update(...)` at 690/704). CPython makes individual ops atomic-ish, so this is a bound-bypass, not a crash, in practice.
- Fix: guard both registries with a `threading.Lock` covering the evict-check-insert sequence and snapshot copies for polling.

**[LOW] `output_delete` can delete a directory a running job is writing into** - `lines 979-1003`
- What: no check against active jobs' `dir` (`_JOBS[*]["dir"]`, `_LIBJOBS[*]["dir"]`). Deleting an in-progress bundle dir makes its thread fail mid-run (and `_snapshot_bundle_job` silently swallows the OSError, so the user sees a generic 500-ish error report).
- Fix: refuse deletion of any path equal to (or a parent of) an active job's output dir.

**[LOW] `/api/settings` accepts arbitrary `library_dir` with no validation** - `lines 333-338`
- What: any string is saved and `_lib_out()` then does `mkdir(parents=True, exist_ok=True)` on it (line 30), creating directories anywhere the user has write permission, and subsequent library writes/scans (`os.walk` in `library_types`, `_publish_to_library` copies) all follow it.
- Fix: validate it's an absolute path on an existing writable volume, reject system roots, and surface mkdir failures instead of silently falling back.

## Missing safeguards
- No upper bound on `count`, `seed` range, `formats`, or `names` list size in `/api/generate`; no batch-count cap in `/api/verify` (CPU-bound `extract_png` per file, only the 100MB body cap limits it).
- `extract_svg` is fed attacker-controlled XML (`data.decode(...)` line 459) — this file can't show whether it's defusedxml/XXE-safe; there should be a test proving no external-entity or entity-expansion processing on uploaded SVGs.
- No test covering `_safe_under_output` with relative `__file__`, `"."`, and `".."` inputs, nor a test that `output_delete` refuses the OUTPUT root and active job dirs.
- `token_validate`/`token_save` return `str(e)` slices to the client; urllib `HTTPError` bodies can echo server-side detail — add a test asserting responses never contain the submitted token.
- No concurrency test for simultaneous `bundle_start` exceeding `MAX_TRACKED_JOBS`, nor for pause→evict→resume of library jobs.
- `zip_selected` lacks an exists-check test for `zipname` collisions.