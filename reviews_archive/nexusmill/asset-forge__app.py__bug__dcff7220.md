# Colibri Review — asset-forge/app.py (bug mode)

- **Source:** C:\Users\User\source\repos\Nexusmill\asset-forge\app.py
- **Twin:** asset-forge-user\app.py is BYTE-IDENTICAL (same sha, verified at dispatch) — this review covers both builds (G23 intact).
- **Model:** claude-fable-5 (in-session, max)
- **sha256:** dcff72205cdd2ce3a31aba9e42b210f8dc2104c7c1371f27f0cc7009fb8e1488
- **Date:** 2026-07-22
- **Mode:** bug
- **Context pack:** jCodemunch outline + importers (none — top-level Flask entry); collaborator sources read: forge/bundle.py (build_bundle ref/None handling, _RunLock via run_job), forge/library_gen.py (build_plan/build_wildcard/prepare_job/_write_job/_run_job_locked), forge/userlib.py (list_items/_INDEX/reference_data_uri), forge/secrets.py (SECRET_KEYS), user-twin forge/tracer stub + templates; docs/remediation_manifest.json (20 asset-forge entries, none against app.py); prior review at 6b58ccc3 superseded, no claims imported.

## Verdict
Solid, defensively-written local app, but NOT clean on money paths: the library generator accepts an unbounded item count straight into paid generation (the exact hazard the bundle path patched and documented), and a picked reference can silently vanish from a paid bundle run. Ship-blocking only for the libgen clamp; the rest are quality-of-defense fixes.

## Bugs & vulnerabilities

**[HIGH] Library-gen start has no count clamp — unbounded paid spend** - `line 879` (libgen_start, 878–899)
- What: `bundle_start` clamps `count` to 1..64 with the comment "unclamped count = unbounded PAID spend" (lines 761–762), but `libgen_start` passes `params["selection"]` uninspected into `_libgen.prepare_job` (line 889). Downstream `build_plan` does `count = int(sel.get("count", ...))` per pack (library_gen.py:88) and `build_wildcard` does `n = int(wc.get("count", ...))` (library_gen.py:108) — no clamp anywhere; `run_job` then generates every pending item with no spend ceiling (only 402/429 pause heuristics).
- Trigger: POST /api/library_gen/start with `{"selection":{"packs":{"geometric":{"types":"all","count":100000}}}}` (or a wildcard count) — a typo'd or hand-crafted local request; /api/library_gen/estimate is advisory and not enforced at start.
- Impact: a single request queues tens of thousands of Replicate generations and starts spending immediately; G19 cost-doctrine violation and an acknowledged hazard (the bundle twin comment) left open on the sibling path.
- Fix: in `libgen_start`, clamp each `packs[*].count` and `wildcard.count` (e.g. 1..64, mirroring line 762) before `prepare_job`, and/or refuse when `len(plan)`/estimate exceeds a hard cap. App-level fix; no call-site breakage (prepare_job signature unchanged).

**[MEDIUM] Chosen reference texture silently dropped from a paid bundle run** - `line 709` (_run_bundle, 706–723)
- What: when `ref_image_id` is set, `_userlib.reference_data_uri(rid)` returns None for any id not in the in-memory `_INDEX` (userlib.py: `_INDEX.get(item_id)`; the index is rebuilt ONLY by /api/userlib/list). Line 711 then clears `ref_cat`/`ref_random` unconditionally, and build_bundle computes `want_ref = bool(ref_category or ref_random_cat or ref_image_uri)` → False → generates with NO reference and no warning.
- Trigger: server restart between opening the library picker and clicking generate (stale page state), or the picked file deleted meanwhile — then the whole paid run executes unreferenced.
- Impact: money spent producing textures that ignore the user's explicit reference choice; no error, no log line.
- Fix: after line 709, if `rid` was provided but `ref_img_uri` is None, fail the job before `build_bundle` ("chosen reference no longer available — reopen the library picker"). No call-site impact.

**[MEDIUM] Libgen resume race: lock-loser marks a RUNNING job "error" on disk** - `line 954` (libgen_control resume, 949–964)
- What: the alive-check (954) and thread assignment (963) are not atomic (`_REG_LOCK` is used for starts but not here; Flask runs `threaded=True`). Two near-simultaneous resume POSTs both see the old thread dead and both spawn `_run_libjob`. The loser's `run_job` raises `RuntimeError` from the non-blocking `_RunLock` (library_gen.py:230–236), which `_run_libjob`'s blanket `except` (860–875) treats as a real failure: it writes `status="error"` + pause_reason into job.json over the winner's live run, saves a spurious error report, and may leave `ent["thread"]` pointing at the dead loser — re-opening the very guard (a third resume passes the alive-check while the winner still runs).
- Trigger: double-clicked Resume button / two tabs; ms-scale window.
- Impact: no double-charge (the file lock holds), but the UI flips to "error" mid-run, an error report is written, and the thread-alive guard is defeated for the rest of the run.
- Fix: wrap 953–964 in `_REG_LOCK`; in `_run_libjob`, catch the lock's RuntimeError distinctly and return without touching the on-disk job (and without an error report).

**[MEDIUM] Redaction coverage gaps: raw exception text bypasses _redact on job surfaces and disk** - `line 749` (also 211, 869, 872)
- What: `_build_error_report` redacts the full report (line 164), but: `_error_payload` puts raw `str(exc)` in `"error"` (211) — returned to the client and, for bundle jobs, persisted unredacted in `BUNDLE_*.job.json` (snapshot keys include "error", 662); `_run_bundle` adds raw `trace=traceback.format_exc()[-800:]` (749) served by bundle_poll; `_run_libjob` writes raw `str(e)[:200]` as pause_reason to the on-disk job.json (869/872) served by libgen_poll.
- Trigger: any provider/OS exception whose message happens to carry a credential or sensitive string (e.g. an echoed request detail); likelihood is scenario-dependent, but the same exception's report IS redacted — the asymmetry is the defect.
- Impact: "secrets never in logs" doctrine hole: unredacted exception text on disk (job snapshots survive restarts, get zipped into support bundles' vicinity) and in API payloads the buyer may screenshot for support.
- Fix: route all four sites through `_redact(...)` (one-line each); coverage then matches the report path.

**[MEDIUM] output_delete refuses FINISHED job dirs, not just running ones** - `line 1051` (1050–1057)
- What: the protected `active` set collects `v["dir"]` from every `_JOBS`/`_LIBJOBS` entry regardless of status, but finished bundle jobs keep `dir` (set at 678, re-set at 735–737) and stay registered until eviction needs room (cap 32, evicted only on new starts). The inline comment states the intent: "never a RUNNING job's dir".
- Trigger: generate a bundle, let it finish, select its folder in the disk-reclaim UI → `{"error": "refused"}` with no reason, until app restart or registry churn.
- Impact: users cannot reclaim disk space for completed runs — the exact purpose of /api/output/delete; looks like data-protection but is a status filter bug.
- Fix: include a `_JOBS` dir only when `v.get("status") == "running"`; for `_LIBJOBS`, only when `v["thread"].is_alive()` (their dirs live under the library root anyway, so `_safe_under_output` already excludes them in default setups).

**[MEDIUM] Bundle→library publish contract broken: three comments promise it, no code does it** - `line 598` (also 41, 455)
- What: `_publish_to_library`'s docstring covers "(<theme> for a bundle)" (41), and `userlib_list`'s comment claims it indexes "LIB_OUT + bundle output" (598) — but the only call site is `generate()` (455), `_run_bundle` never publishes, and `userlib_list` passes exactly `[_lib_out()]` to `_userlib.list_items(roots)` (userlib.py:22 scans only the given roots; its module docstring also promises "any of their own bundles").
- Trigger: generate any AI bundle, open the reference picker (/api/userlib/list) → bundle textures absent; they can never be chosen as references (the picker's stated purpose) unless manually filed via /api/library/file.
- Impact: advertised own-bundle-as-reference flow silently unavailable; stale contracts on three sites will mislead the next editor.
- Fix: either call `_publish_to_library(out_dir, theme)` in `_run_bundle` after success (matching the docstring; copies pre-stamp CLEAN files — note _zip_dir stamps in place at 634, so publish must run BEFORE _zip_dir), or fix all three comments and the picker claim. Decide, don't leave the split.

**[MEDIUM · PLAUSIBLE] Windows: job.json atomic replace can collide with a concurrent poll read and kill a paid run** - `line 925` (with library_gen.py:197)
- What: `libgen_poll` opens `job.json` (`load_job`, every UI poll) while the worker checkpoints via `tmp.replace(job.json)` (library_gen.py:194–197). On Windows, CPython opens files without FILE_SHARE_DELETE, so MoveFileEx-with-replace fails with PermissionError if a reader holds the file at that instant; `_write_job` calls inside `_run_job_locked` are unguarded, so the exception aborts the run and `_run_libjob` marks the job "error" (resumable, plus a spurious error report).
- Unverified because: requires Windows runtime to confirm the sharing-violation timing; mechanism is standard Win32 semantics and the primary platform IS Windows (repo lives under C:\Users\User).
- Fix: retry `tmp.replace` briefly on PermissionError in `_write_job` (library_gen side); nothing to change in app.py's reader.

**[LOW] User build emits tracer language: line 497 discards the stub's message** - `line 497` (_verify_one)
- What: the user-twin tracer stub returns `(None, "provenance tracing is not part of this build")` from extract_png/extract_svg precisely so no tracer wording surfaces — but `_verify_one` ignores `src` on the no-token path and hardcodes `{"status": "CLEAN", "detail": "no tracer recovered"}`. The user build's templates never call /api/verify (0 references), but the endpoint is live and answers with tracer language (doctrine: no watermark/tracer language in end-user surfaces).
- Trigger: any POST to /api/verify in the asset-forge-user build (from the app origin).
- Impact: doctrine leak of the provenance concept in the end-user product; also masks the stub's honest "not part of this build" message.
- Fix (keeps twins byte-identical and both builds correct): `return {"status": "CLEAN", "detail": src or "no tracer recovered"}` — creator build keeps "no tracer found" (png_stego.py:170), user build shows the stub's wording.

**[LOW] _SECRET_RE cannot redact Hugging Face tokens though HF_TOKEN is a managed secret** - `line 94`
- What: the redaction regex covers r8_/sk-/gsk_/Bearer/AKIA but not `hf_[A-Za-z0-9]{6,}`, while forge/secrets.py:21 lists HF_TOKEN in SECRET_KEYS (managed, migrated, scrubbed elsewhere).
- Trigger: an HF token appearing in any exception/report text (dormant today — imagegen uses Replicate/Groq — but the secret store explicitly handles it).
- Impact: the one managed secret class the redactor cannot catch.
- Fix: add `hf_[A-Za-z0-9]{6,}` to `_SECRET_RE`.

## Missing safeguards
- No total-spend ceiling on any generation path — only per-request count clamps (bundle) and 402/429 pause heuristics; a per-job hard budget (from the G19 estimate the user saw) would bound worst cases.
- `preview` 500s on missing/non-numeric `seed` (line 426 `int(d["seed"])`), `generate` on non-numeric seed (452) — inconsistent with the clean 400 given for `count`; validate like count.
- `libgen_control` resume accepts a `model` override (961) without updating the on-disk `job["model"]` — mid-job model switch generates a mixed set and prices `spent_est` from the OLD model's catalog entry (library_gen.py `_run_job_locked` price lookup).
- `bundle.regen_from_recipe` exists (bundle.py:207) but no app route calls it — errored bundle runs can only be fully re-bought from the UI despite recipes being written for exactly this.
- `_snapshot_bundle_job` (667) and `_publish_to_library` (68) deliberately swallow OSError — acceptable best-effort, but a debug-level breadcrumb would make persistent snapshot failures diagnosable.

## Phase 3 note
All findings above are CONFIRMED by end-to-end trace except the Windows replace/read collision, kept as PLAUSIBLE with the unverified-because note. Refuted and deleted during verification: bundle count clamp "missing" (exists at 762), `_lib_slug`/`_re` definition-order NameError (module import completes before first request), `_write_job` non-atomicity (tmp+replace IS atomic), snapshot-read torn JSON in bundle_history (reader catches and skips), >2000-item userlib truncation as a ref-drop trigger (unlisted ids can't be picked).
