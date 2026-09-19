# Colibri Review - bug (FULL re-audit) - asset-forge/templates/index.html

- **Source path:** `asset-forge/templates/index.html` (byte-identical twin `asset-forge-user/templates/index.html`, G23 - every fix applies to both)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (Asset Forge stale units), rank 44
- **sha256 reviewed:** `d96d25b9cd232aa4948141d7dd395b279325e71d9c6c5325959e3dc298214881` (sha8 `d96d25b9`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 2026-07-22 review and the 08-25 debug record predate the adversarial gate and are untrusted - no delta against them)
- **Context pack:** jCodemunch `get_file_outline` of `asset-forge/app.py` (every route the page calls) + `get_symbol_source` of `_origin_guard`, `options`, `bundle_start`, `bundle_estimate`, `bundle_poll`, `bundle_control`, `_run_bundle`, `_error_payload`, `_evict_finished`, `library_file`, `userlib_*`, `asset_file`, `open_dir`, `token_*`, `vault_*`, `styles_save`; `search_text` for `_publish_to_library(` callers and replicate_flux's HTTPError handling; the remediation rows (AF-BUNDLE-ALPHA, AF-SCHEMA-UI, PROMPT-DOCTRINE-UX, AF-OUTPUT-KNOBS, UI-1/UI-3) and the features registry rows naming the template, loaded as CLAIMS; the prior records `index.html__bug__bcd1664b.md` (07-22) and `__debug__d96d25b9.md` (08-25) as claims; DESIGN_BIBLE R1/R2/R6/R7 + G19/G20. Every line of the 826 read.

## Verdict
Shippable after six fixes; the token/vault flows, the transparency picker's three honest zero states, the schema panel (R1/R2), the esc()-everywhere discipline on gallery/library/prompt rows and the same-origin fetch contract with `_origin_guard` all hold at the bytes. The defects are one FALSE product claim on the card, the two sinks that skip esc(), a poll loop with no exit for two real states, a count label that does not say what will run, and the stale price literals the UI-1 remediation said were gone.

## Bugs & vulnerabilities

**[MEDIUM] The Studio card promises "everything you generate here is added to your library automatically" - it is not** - `line 90`
- What: the hint row states automatic library filing. `_publish_to_library` is called by exactly one route, the legacy `/api/generate` (app.py:803); the Studio's real path `/api/bundle/start` -> `_run_bundle` never files anything - filing is opt-in through the "Save selected / Save all" bar the page itself renders (`library_file` docstring: "Opt-in (nothing is auto-filed)"). The row is also a static note field (R1).
- Trigger: every Studio run.
- Impact: a customer reads that their textures are in the Pattern Skin library, does not press Save, and finds nothing there (G11 truth on a shipped surface).
- Fix: delete the row (the save bar already says what happens). Battery `IDX_studio_autoadd_claim_true_or_absent` RED->GREEN.
- Verification: CONFIRMED (`search_text` shows the single caller; `_run_bundle` source has no publish call).

**[LOW] `fail()` and the running-log line render server strings through innerHTML unescaped** - `lines 755, 759`
- What: every other dynamic row goes through `esc()`; these two concatenate `msg` / `j.log` straight into innerHTML. `msg` is `r.error` / `j.error` = `_error_payload`'s `_redact(str(exc))` - the raw exception text, which the server hands through verbatim (proved: a stubbed provider raising `<img src=x onerror=..>` arrives in the poll as-is). Provider error bodies reach `str(exc)` in the create path (replicate_flux reads the response `body`, line 292) - external data into a markup sink inside the pywebview origin that can call every local route.
- Trigger: a provider/server error whose text carries markup.
- Impact: markup executes in the app origin (spend, delete outputs); today's realistic case is self-echo, the provider-body case is PLAUSIBLE (the exact raise line embedding the body was not traced).
- Fix: `textContent` in `fail()`, `esc(j.log...)` in the log line. Battery `IDX_error_text_is_data_not_markup` RED->GREEN.
- Verification: CONFIRMED for the sink and the pass-through; PLAUSIBLE for the external-body trigger.

**[LOW] `checkJob()` has no exit for 'cancelled' or a vanished job - the 2 s poll runs forever with Generate disabled** - `lines 750-758`
- What: the branches are running / done / error. A job cancelled through `/api/bundle/control` (the registry row AF-BUNDLE-EXT names it; this page has no cancel button but the API is live) or a 404 `{error:"no such job"}` after an app restart or a registry eviction (`_evict_finished` drops finished jobs when 32 are tracked) leaves `j.status` unmatched: the interval keeps firing, the spinner says "starting…", Generate stays disabled until a reload.
- Fix: a fall-through branch that clears the interval and reports (`fail(j.error||'job '+status+' - nothing more will arrive')`). Battery `IDX_poll_ends_on_cancelled_or_missing_job` RED->GREEN.
- Verification: CONFIRMED (bundle_poll 404 traced; bundle_control sets status 'cancelled').

**[LOW] The Generate label counts the typed number, not what the server will run** - `lines 474-483`
- What: `/api/bundle/estimate` and `/api/bundle/start` both clamp `count` to 1..64 and the estimate returns the clamped `count`; the label uses the raw `n` (the input's max=50 is only a browser hint). Typed 100: the button reads "Generate 100 textures - ~$1.60" and the run makes 64. Typed 0: `parseInt||8` prices 8, the run makes 1.
- Impact: the price is never under-quoted (safe direction), the count promise is wrong (R7 says the control states what the click does).
- Fix: label from `e.count` when present. Battery `IDX_count_label_uses_server_count` RED->GREEN.
- Verification: CONFIRMED (estimate returns count=64 for 100).

**[LOW] The pricebar ships hardcoded per-image prices as a fallback and shows them when the catalog has no prices** - `line 292`, `boot()` 320-324
- What: UI-1 (2026-07-31) said "one price source - the catalog - never a hardcoded list again", yet the select still carries eight literal prices ("flux-dev $0.025 / image" - the very value UI-1 called stale). `boot()` replaces them only when `OPT.model_prices` has keys; `options()` returns `{}` on any catalog load failure, so the stale literals then stay on screen as current prices (G19).
- Fix: an empty select + "—" placeholder; hide the row when no catalog prices arrive. Battery `IDX_pricebar_has_no_stale_literals` RED->GREEN.
- Verification: CONFIRMED (options() except-path returns `model_prices: {}`).

## Missing safeguards
- `onbValidate` shows `r.error` = `str(e)[-160:]` from `_validate_replicate`; a token with a non-latin-1 character makes urllib raise with the value in the message (the class PS-RC-TOKEN-SENDABLE fixed in Pattern Skin today) - textContent, so display-only; app.py's concern, out of unit.
- `startBundle` posts `count` as the raw string; the server parses it (clean 400 on garbage) - fine, noted.
- `refreshGenPrice` swallows a 400 from the estimate (`catch(e){}`): the label drops its price but Generate stays enabled; the start then repeats the same 400 through `fail()`. Acceptable, but the refusal could ride the label.
- `_dlOne` relies on `<a download>` clicks - behaviour inside pywebview/WebView2 unverified here.

## Adversarial verification pass (refuted claims)
- "syncOutputKnobs fires refreshGenPrice before syncTransparencyModels switches the model - the stale-model price can land last" - refuted: the first estimate is issued before the transparency chain's slow fetch (up to eight schema reads + applyModelSchema) and resolves first in practice; the chain re-prices at its end.
- "renderMopts ids built with esc(p.name) via innerHTML diverge from the `'sx_'+p.name` lookup" - refuted: the HTML parser decodes the entities back, the ids are equal.
- "Fetches lack the Origin/CSRF contract `_origin_guard` enforces" - refuted: every mutating call is a same-origin POST; browsers (WebView2 included) send Origin on same-origin POSTs, the guard admits local origins.
- "`it.seed` / `j.zip` / `CURRENT.dir` reach innerHTML unescaped" - refuted: seed is an int, the zip and dir names are server-built from an alnum slug + stamp + job id.
- "`/api/userlib/thumb/${esc(it.id)}` is traversable" - refuted: ids are server-derived; the route resolves through `_userlib.thumb_uri`, not a path join.
- "The prompt library injects into the theme" - refuted: values go through `Option()`/`.value`, never innerHTML; the data is shipped by us.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `e4f34080d1f4ecd8ceff16c9fb4821afbf7ffae1c9b90811a3510b97f14cc13e`. Rows AF-IDX-LIBRARY-CLAIM, AF-IDX-UNESCAPED-SINKS, AF-IDX-POLL-EXIT, AF-IDX-CLAMPED-LABEL, AF-IDX-PRICEBAR-LITERALS in `docs/remediation_manifest.json`, same commit.

