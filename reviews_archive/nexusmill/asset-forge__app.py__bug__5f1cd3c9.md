# Colibri Review - bug (DELTA) - asset-forge/app.py

- **Source path:** `asset-forge/app.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 13
- **sha256 reviewed:** `5f1cd3c9ad418542e0adf831a095d4af8625baf3d49d493675518a4082312c2d` (sha8 `5f1cd3c9`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `2d557bd3` (2026-07-24 round 4)
- **Delta reviewed:** 12 commits / 627 diff lines: 15a8e8e8 (`_request_seed`), 9892fd93 (HM-EXCISE textures/ + FLAG-REGEN endpoints), d0d57fc3 + fce72ead + 787cfc65 (GROK-APP billing/containment/allow-list), ae8fc346 (GROK-APP6 resume model + `_FLAT_LOCK` on library writes), 0e9adaff + e2266724 + 516f0d44 (KV-3/4 vault endpoints, `_vault_err`), 5a2374b5 + 265cbc59 + 7696f887 (AF-BUNDLE-ALPHA native-only transparency, `_bundle_output_route` shared by estimate and start) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json`, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the symbols each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta (the creator/user twin is byte-identical, G23). Estimate and start share one routing helper so they cannot disagree; the bundle path refuses an unpriced model before any thread starts; resume re-reads the job's recorded model; library writes serialise the exists-then-write under `_FLAT_LOCK` taken AFTER `_lib_out()` (no re-entrancy); `output_delete` refuses by containment.

## Bugs & vulnerabilities
None confirmed at the delta.

## Notes
- "`libgen_regen` hands the raw client body to `prepare_regen_job`, bypassing the GROK-APP #2 allow-list so an unpriced knob could reach the job" - REFUTED: `prepare_regen_job` (`library_gen.py:780-817`) reads only `output`, `aspect_ratio`, `seamless` and `schema_extra` from `params` and prices through the same `estimate(..., prompt_upgrade=False, opts=...)` the regen_estimate endpoint calls.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - asset-forge/app.py

- **Source path:** `asset-forge/app.py` (twin `asset-forge-user/app.py` byte-identical at this sha, G23 - every fix applies to both)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 13
- **sha256 reviewed:** `5f1cd3c9ad418542e0adf831a095d4af8625baf3d49d493675518a4082312c2d` (sha8 `5f1cd3c9`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: every prior record of this file - 07-19..08-23 rounds, the 08-23 GROK-APP6 gate included - predates the adversarial gate and is untrusted; no delta)
- **Context pack:** all 1815 lines read; jCodemunch `get_file_outline` (0 importers - the launcher/pywebview starts it by module); the 19 remediation rows, the 7 deferred dockets and the 26 feature-registry rows naming the file loaded as CLAIMS; `get_symbol_source` on `config.save_provider` / `load_providers`, `schema.capabilities`, `library_gen.prepare_job` / `prepare_regen_job`; `search_text` on `templates/index.html` (what the Studio actually sends: `seed:document.getElementById('seed').value`, `ref_strength`, no `buyer_name`); the user build's `forge/tracer/__init__.py` stubs; the existing `tests/harness/probes/af_transparency_probe.py` pattern.

## Verdict
Shippable after the two fixes below. The route surface holds at the bytes: the origin/host guard refuses foreign or missing Host, `Sec-Fetch-Site: cross-site`, foreign Origin/Referer and origin-less mutating verbs; every path under OUTPUT goes through `_safe_under_output` (resolve + containment) and `output_delete` refuses by containment against the resolved library, error_reports and every LIVE job dir; every paid start is priced by the same helper its estimate uses and refuses unpriced models before any thread; the token is written to the encrypted store (KV-5), every exception surface is redacted; `_clean_schema_extra` keeps the dynamic panel away from seed/num_outputs/reference wiring. The one paid path that still trusts a raw client value is the bundle seed.

## Bugs & vulnerabilities

**[MEDIUM] `/api/bundle/start` never validated `seed`; a cleared Studio seed box registers a job that dies as an error report** - `bundle_start` line 1171-1209, consumed at `_run_bundle` line 1120
- What: the Studio posts the seed field verbatim (`index.html:728` - a `type=number` input's `.value` is the string `""` once the user clears or mistypes it). `bundle_start` clamps `count`, sanitises `schema_extra`, prices the model, gates the token - and passes `seed` straight through. The worker thread then evaluates `int(params.get("seed", 1000))` in the `build_bundle` call and raises `ValueError` before any spend.
- Trigger: clear the Seed box (or type anything non-numeric) and click Generate on a bundle.
- Impact: a job is registered and flips to `status=error` with a support payload (`error_id`, `report_file`, a diagnostics zip written to `output/error_reports/`) for a typo - the same class the 2026-08-11 remediation fixed on `/api/preview` and `/api/generate` via `_request_seed`; the paid path was left out. No money is lost (the `int()` runs before `build_bundle`), but the user gets the "send this to support" flow instead of a field error, and each attempt writes a report + zip.
- Fix: validate in the route with the existing helper - `params["seed"] = _request_seed(params)` inside `try/except ValueError -> 400` (omitted/empty = a fresh internal seed, malformed = 400 "seed must be an integer"). Explicit seeds are unchanged (`_run_bundle` still reads `params["seed"]`); the Studio always sends its default 1000, so UI reproducibility is unchanged. Snippet 1 in `fix_snippets_af_app.json`.
- Verification: CONFIRMED - `probe_af_app_1.py` sections `AF_bundle_start_rejects_malformed_seed` (200 + job today) and `AF_bundle_start_empty_seed_runs` (status=error "invalid literal for int() with base 10: ''" today) RED on the current bytes; GREEN on a scratch copy carrying the snippet, with `AF_bundle_start_int_seed_kept` proving explicit seeds still reach `build_bundle`.

**[LOW] Transparent output on an UNREACHABLE schema is reported as "model cannot produce transparent output natively" (G20)** - `_bundle_output_route` line 1305-1310 (surfaces from both `/api/bundle/estimate` and `/api/bundle/start`)
- What: `capabilities()` reports `transparency_param=None` for an empty (unreachable) schema by design - conservative, correct. The route turns that into the incapability copy without looking at `has_schema`, which `capabilities()` sets False in exactly this case.
- Trigger: the Studio's emblem default is Transparent (`_oo.normalize` defaults emblem background to transparent); on a fresh install with no schema cache, or with Replicate unreachable, the very first estimate for a capable model reads "cannot produce transparent output natively - pick a transparency-capable model" (reproduced against the real code path before the probe stubbed `_caps`).
- Impact: G20 says an unreachable model greys with "temporarily unavailable + recheck", never a false capability claim; a user is told to abandon a model that can do it, and `/api/transparency_models` (which counts `unreachable` for the picker) disagrees with the estimate line.
- Fix: branch on `caps.get("has_schema", True)` before the incapability message - "model %r's input schema is unreachable right now, so native transparency cannot be confirmed - recheck with the picker's refresh once online, or choose a white/black/full-bleed background". Same ValueError, same 400, both endpoints. Snippet 2.
- Verification: CONFIRMED - `AF_transparent_estimate_names_unreachable_schema` RED today, GREEN on the patched copy; `AF_transparent_estimate_still_refuses_incapable` guards the reachable-but-incapable message.

## Missing safeguards (not fixed)
- Stale copy: the three "no Replicate token in ~/.asset-forge/providers.env" refusals (`bundle_start`, `libgen_start`, `libgen_regen`) name a file that is import-only since KV-5 (`save_provider` writes the encrypted store and scrubs it); a token typed into that file still works once (migrate_legacy lifts it), so it misleads without breaking - the message should point at the Studio's token box / vault.
- `_flatten_library` acts on WHATEVER folder `/api/settings` sets as `library_dir`: loose root images are moved into `textures/` and sub-folders under an existing `textures/`/`emblem/` are flattened on first sight (the two owner-authorised "safe cases", 2026-08-01). A pre-existing personal folder chosen as the library gets reorganised without a prompt; `settings_set` could warn when the chosen folder already holds loose images.
- `library_dir` set INSIDE OUTPUT (or to OUTPUT itself) makes every output set undeletable by containment - self-inflicted configuration, no data risk.
- Crafted-body 500s only reachable by hand-built requests on the local socket (non-string `buyer_name`/`theme`/`output`/`selection`, `formats: null`): the JSON error handler answers with a clean 500 + report - noise, not exposure.
- `libgen_poll` 500s (one error report per poll) if a tracked job's folder under `.af_jobs` is deleted by hand while the entry lives; the UI stops polling on the first error.
- G14 note for the owner (not a code defect): the user build keeps `/api/verify` (stubbed - always CLEAN / "provenance tracing is not part of this build") and reports `creator_id: "local"` + an empty fingerprint in `/api/options`; nothing markets it, but it is provenance vocabulary on a customer surface.

## Adversarial verification pass (refuted claims - not findings)
- "`_safe_under_output("")` lets `/api/library/file`, `/api/open_dir`, `/api/zip_selected` operate on the OUTPUT root" - refuted: the root holds only set dirs and zips; `library_file` skips non-raster, `open_dir` opens a folder the user owns, `output_delete` refuses the root explicitly.
- "A junction inside OUTPUT pointing at the library escapes `output_delete`'s containment" - refuted: `_safe_under_output` resolves and refuses anything outside OUTPUT; a junction resolving to the library equals `_lib` and is blocked before `rmtree`.
- "`model_schema` returns `str(e)` unredacted - a token could leak" - refuted: `get_schema` raises `HTTPError`/`URLError` whose text carries no request headers; no path puts the token into an exception message.
- "A foreign page can drive `GET /api/transparency_models?refresh=1` (49 schema fetches)" - refuted: browsers send `Sec-Fetch-Site: cross-site` on subresource GETs and the guard 403s it; an Origin-bearing fetch is refused as well.
- "`token_save` writes the key in plaintext (G18)" - refuted: `config.save_provider` writes the encrypted store and scrubs `providers.env`; only the user-facing message is stale (note above).
- "Racing resumes double-spend" and "`libgen_regen` hands the raw body past the allow-list" - refuted again at the bytes (`_RunLock` makes the loser a benign return; `prepare_regen_job` reads four named keys and prices through `estimate()`).

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `7592c8aba7a1d7d1675c98efb7bf03d067235ca851d44a59f75a54fe6435ac52`. Rows AF-BUNDLE-SEED-VALIDATE, AF-ALPHA-UNREACHABLE-COPY in `docs/remediation_manifest.json`, same commit.

