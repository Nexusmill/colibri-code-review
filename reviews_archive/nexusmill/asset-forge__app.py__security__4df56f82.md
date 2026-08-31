# colibri gate — asset-forge/app.py (grok round 6, security)

- **source:** asset-forge/app.py (+ asset-forge-user twin, G23)
- **model:** grok-4.6 security (external, .grok_reviews/2026-08-22_app_grok46.md) gated in-session by claude-fable-5
- **sha256:** 4df56f82a3b79733... (current bytes at dispatch, G36)
- **date:** 2026-08-22 · **mode:** security (grok round 6; delta vs kimi/glm/GROK-APP/single-HC history pre-declared)
- **context pack:** money/security invariants + closed GROK-APP items + the rejected _JOBS background-thread architecture + the stale thumb-traversal all pre-declared; verified libgen_control/regen/start + libgen_regen_estimate + prepare_regen_job + the library write sites.

## Verdict
One real HIGH billing bypass on resume; Grok's second HIGH refuted; the TOCTOU downgraded
to LOW on reachability.

## Findings after adversarial verification

**[HIGH, CONFIRMED — billing bypass] `libgen_control` resume takes the model from the request body with NO pricing gate** — libgen_control:1554-1557
- Verified: on `action=="resume"`, `model = d.get("model") or load_job(...).get("model","flux-schnell")` and `_run_libjob(job_id, dir, model)` is spawned directly. Unlike `libgen_start` (which builds an allow-listed dict and calls `prepare_job` → `estimate()` → refuses an unpriced model with a clean 400) and unlike `/estimate`, resume goes through NO catalog/price check and NO re-estimate. A `POST /api/library_gen/control/<paused_job>` with `{"action":"resume","model":"<any/expensive/unpriced slug>"}` bills every remaining image at that model — bypassing the GROK-APP unpriced-model 400 and breaking G19 (shown estimate ≠ billed basis). The `"flux-schnell"` literal fallback also disagrees with the catalog default the start/estimate paths use.
- Fix (Grok's, sound): on resume ignore the body model — use the on-disk job's recorded model; if a model switch is ever a real feature, refuse unless the slug is priced in `catalog_summary()` and re-price the remaining work with the same `estimate()` as `/estimate`.

**[LOW, CONFIRMED — downgraded from Grok's MEDIUM] check-then-write TOCTOU can silently replace a library texture** — `_publish_to_library`:270-271 (`if _target.exists(): continue … _target.write_bytes`), `library_file`:911-916 (`if (dst/tn).exists(): skipped … shutil.copy2`)
- Verified the pattern: both do exists()-check then write/copy without a lock; `_migrate_folders` holds `_FLAT_LOCK` but these two do not. Two concurrent writers to the same flat name → the "don't silently replace" guard races and one overwrites.
- Downgraded to LOW: single-user local desktop app; the collision needs two overlapping requests targeting the IDENTICAL flat name (job-writer names are slug+seed, manual-file names are type+name — distinct namespaces), so the window is narrow. Real "never silently replace a paid asset" pattern worth an `os.open(O_CREAT|O_EXCL)` + suffix-bump hardening (and holding `_FLAT_LOCK` around these dest creations), but not a MEDIUM on reachability.

## Refuted and dropped
- **HIGH (Grok) — `libgen_regen` forwards raw `params` to `prepare_regen_job` → unpriced knob changes the charge — REFUTED.** Traced: `prepare_regen_job` does NOT merge the body; it reads only `output`/`aspect_ratio`/`seamless`/`schema_extra` from params, pins `prompt_upgrade=False`, and re-runs `estimate(plan, model, prompt_upgrade=False, opts=normalize(output))` — the IDENTICAL call `libgen_regen_estimate` uses. So the shown price equals the job's recorded estimate equals the billed basis regardless of extra body keys; the extra keys are inert. Unlike `/start`'s `prepare_job` (which needed the route-level allow-list), the regen callee already allow-lists internally. At most a stylistic inconsistency (route-level vs callee-level allow-listing), not a billing defect — not docketed.
