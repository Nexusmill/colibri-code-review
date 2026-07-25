# BUG review: asset-forge-user\app.py

- source: `C:\Users\User\source\repos\Nexusmill\asset-forge-user\app.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 19:30
- tokens: in 11488 / out 3981
- est cost: $0.0942

---

## Verdict
Shippable for a local-only tool, but not clean: the in-memory job registries can silently drop *running* jobs (users get 404s mid-generation while Replicate credits keep burning), and several error paths crash on malformed data instead of degrading gracefully. Biggest single risk: `/api/verify` and the job-eviction logic turn expected edge cases into 500s or lost work.

## Bugs & vulnerabilities

**[HIGH] Job eviction drops running jobs, orphaning threads and stranding users** - `lines 583-584, 647-648`
- What: `while len(_JOBS) > 32: _JOBS.pop(next(iter(_JOBS)))` evicts the oldest entry regardless of `status`. A job with `status: "running"` is evicted exactly like a finished one.
- Trigger: 33 bundle (or library-gen) jobs started in one session; the 33rd start evicts job #1 even if it's still generating.
- Impact: `bundle_poll`/`libgen_poll` return 404 for a job whose thread is still running and still spending Replicate credits; the user loses progress, cancel/pause control, and the result. `_run_bundle` keeps a stale dict reference so the work completes invisibly. Same for `_LIBJOBS`, where eviction also removes the `control` dict, making pause/cancel impossible while `_run_libjob` still reads `ent["control"]` (a captured reference, so the job runs unkillable).
- Fix: only evict entries with `status in ("done", "error")`; refuse new jobs (429/400) when 32 are active.

**[HIGH] Duplicate concurrent library jobs on the same output dir via "resume"** - `lines 679-685`
- What: `resume` unconditionally spawns a new `_run_libjob` thread for `ent["dir"]` with no check that the previous thread actually exited (a paused job's thread may still be alive mid-iteration, and "resume" can be clicked twice).
- Trigger: user hits resume while the old thread is still winding down, or double-clicks resume.
- Impact: two threads run the same job directory concurrently → duplicated Replicate API spend, interleaved writes to the same job state file / output images (corruption), and both threads share one `control` dict so cancelling one cancels neither cleanly.
- Fix: track a per-job `thread_alive` flag (or `threading.Event`); reject resume if a thread is active.

**[MEDIUM] `/api/verify` crashes with KeyError on manifests lacking `set_id`** - `line 407`
- What: `if m["set_id"] == r["set"]` sits *outside* the `try/except` that only guards `json.load`. A manifest that parses but lacks `set_id` (hand-edited, older format, or the check at line 407 uses a raw key while line 404's file handle is also never closed — see below) raises `KeyError`.
- Trigger: any `output/**/SALE_*.manifest.json` or `BUNDLE_*.manifest.json` without a `set_id` key, encountered before the matching one.
- Impact: 500 instead of a verification result; also `json.load(open(mf))` leaks a file handle per iteration (never closed).
- Fix: `m.get("set_id")`; use `with open(mf, encoding="utf-8") as fh:` or `Path(mf).read_text()`.

**[MEDIUM] `/api/generate` set-dir/zip collision on same-second requests** - `lines 343-346, 354`
- What: `stamp = ...strftime("%Y%m%d_%H%M%S")` has 1-second resolution and `set_dir`/`zip_path` contain no unique component (unlike `_run_bundle`, which appends `job_id`). With `threaded=True`, two concurrent `/api/generate` calls with the same label+family write into the same directory and zip.
- Trigger: double-click, retry, or two browser tabs posting within the same second.
- Impact: interleaved/overwritten textures, a zip mixing both runs, wrong manifest returned to one caller; `_personalize.stamp_dir` may stamp half-written files.
- Fix: append `uuid.uuid4().hex[:8]` to `set_dir` (mirroring the bundle path).

**[MEDIUM] Unbounded upload read in `/api/verify`** - `line 379`
- What: `data = f.read()` with no size cap; `extract_svg(data.decode(...))` and `tmp.write_bytes(data)` process it all. Also `f.filename` can be `None` for a malformed multipart part → `AttributeError` on `.lower()`.
- Trigger: a multi-GB "PNG" upload, or a file part without a filename.
- Impact: memory exhaustion of the local server (DoS of the user's own app), or a 500.
- Fix: `data = f.read(MAX_BYTES)` with a sane limit (e.g. 50 MB) and `name = (f.filename or "").lower()`.

**[MEDIUM] Origin guard has bypass gaps** - `lines 91-106`
- What: Three holes: (1) `if request.host and ...` — a request with no/empty Host header skips the check entirely; (2) `Sec-Fetch-Site: same-site` is accepted, so any page served from a `*.localhost` subdomain or same-site context can POST freely; (3) for state-changing POSTs the Referer check is *optional* (`if ref and ...`) and Origin is absent for some same-origin-navigated requests — the guard depends entirely on browser-sent headers that non-browser attackers omit but malicious web pages on `*.localhost` variants can satisfy.
- Trigger: malicious page hosted on `anything.localhost` (resolves to 127.0.0.1) issuing `fetch("http://127.0.0.1:5000/api/bundle/start", ...)` — `Sec-Fetch-Site` is `same-site`, Origin netloc is `*.localhost`-suffixed but `foo.localhost` fails `_is_local_netloc` → blocked; however `localhost` subdomain handling varies by browser, and plain `same-site` fetches from an attacker page on another local port of the same registrable site pass.
- Impact: cross-site pages could drive the API and burn Replicate credits in the gap cases.
- Fix: treat *missing* Host as forbidden; require `Sec-Fetch-Site in (None, "same-origin", "none")` for POST; optionally add a per-session random token header checked server-side.

**[LOW] `_thumb_b64` leaks image file handles** - `lines 497-501`
- What: `_I.open(path)` is never closed; CPython GC usually collects, but on PyPy/Windows the handle lingers.
- Trigger: repeated bundle jobs with many items.
- Impact: file-descriptor exhaustion over a long session.
- Fix: `with _I.open(path) as im: im = im.convert("RGB"); ...`

**[LOW] `library_file` precedence/readability bug and unguarded per-file copy** - `lines 436, 459`
- What: `if not ptype or ptype == "misc" and not str(d.get("type","")).strip():` — `not ptype` is dead code (`_lib_slug` never returns falsy), and `and` binding makes the intent fragile; a type that *slugs to* `"misc"` (e.g. `"???"`) is rejected only because the raw string is non-empty... actually it is *accepted* (second clause false) yet files into `misc/` — arguably wrong. Separately, `(dst / n).write_bytes(...)` is unguarded: one unwritable file aborts the whole loop mid-way with a 500, leaving a partial copy reported as nothing.
- Fix: rewrite as `if not raw_type or _lib_slug(raw_type) == "misc" and raw_type slugs to misc only when empty`; wrap the copy in try/except and count failures.

**[LOW] Relative-path glob in `/api/verify` depends on CWD** - `lines 401-402`
- What: `glob.glob("output/**/SALE_*.manifest.json", ...)` is relative to the process working directory, not `BASE`. Launching the app from any other directory silently finds zero manifests → buyer info always `None`.
- Fix: use `OUTPUT.glob("**/SALE_*.manifest.json")` etc.

**[LOW] `libgen_poll` trusts on-disk job file keys** - `lines 658-659`
- What: `job["done"]`, `job["total"]`, `job["failed"]` are raw key lookups on a JSON file written by another thread / previous run; a truncated or older-format job file raises `KeyError` → 500 on every poll.
- Fix: `.get(...)` with defaults, or validate schema in `load_job`.

**[LOW] Bundle progress reports `done = i - 1`** - `line 526`
- What: `job["done"] = i - 1` means after image `i` *starts*, done shows `i-1`; the UI reads 0 for the entire first image and the run only shows full progress via the final `job.update(done=m["count"])`. Minor correctness/UX; also `total`/`done` mutate from worker thread while Flask reads them — benign under GIL but racy for the dict `update()` (fine, atomic) — just noting the off-by-one.
- Fix: `job["done"] = i` after completion of image `i` (callback currently fires before generation — document or rewire).

## Missing safeguards
- No rate limiting / concurrency cap on `/api/generate` and `/api/bundle/start` — one client can spawn unlimited threads and Replicate spend (only memory is bounded, and the bound itself is buggy — see HIGH #1).
- No size/count validation on `count`, `seed`, `names[]` in `zip_selected`/`library_file` — a 100k-entry `names` list forces 100k `resolve()` syscalls per request.
- No tests for `_safe_under_output` edge cases (symlinks inside `output/` pointing out, `..` names in `zip_selected`, case-insensitive Windows paths).
- `_origin_guard` has no test coverage; given it's the only CSRF/DNS-rebinding defense, regression tests for missing Host, `same-site`, and IPv6-bracket hosts (`[::1]:5000` currently fails the split — legitimate local requests from literal IPv6 get 403).
- `settings_set` accepts any `library_dir` string with no validation that it's writable or not a system path; combined with `_publish_to_library` this writes generated files anywhere the local user can.
- Error-report zips and error `.txt` files accumulate in `output/error_reports/` forever — no rotation/cap.
- `_verify` SVG path does no XML safety check before `extract_svg` (assumes downstream parses defensively — worth a test with a billion-laughs/XXE payload against the tracer's SVG parser).