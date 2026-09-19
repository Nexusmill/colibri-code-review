# Colibri Review - bug (FULL re-audit) - asset-forge/templates/library.html

- **Source path:** `asset-forge/templates/library.html` (byte-identical twin `asset-forge-user/templates/library.html`, G23 - every fix applies to both)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (Asset Forge stale units), rank 45
- **sha256 reviewed:** `99cc6d36a22461d50472e80b465cd63d4b44f23ce0316e83681cca62cbd73abe` (sha8 `99cc6d36`) - the PRE-fix bytes
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 2026-08-04 round-1 review predates the adversarial gate and is untrusted - no delta against it)
- **Context pack:** jCodemunch outline of `asset-forge/app.py` + sources of `libgen_estimate`, `libgen_start`, `libgen_poll`, `libgen_control`, `libgen_flagged`, `libgen_regen`, `libgen_regen_estimate`, `_origin_guard`, `_json_error_handler`; the remediation rows (LIB-KLEIN-WARN, AF-SCHEMA-UI, AF-LIB-KNOBS, AF-FLAG-REGEN, UI-1, DOCTRINE-4, MODEL-SWEEP) and registry rows (AF-FLAG-REGEN, AF-LIB-KNOBS, AF-KLEIN-CAVEAT, AF-UI-TOKENS) as CLAIMS; the prior record `library.html__bug__384485ed.md` as a claim; DESIGN_BIBLE R1/R2/R6/R7 + G19/G20. Every line of the 570 read.

## Verdict
Not shippable as the regeneration path stands: regenerating while a run is in flight takes the running job's controls away while it keeps spending. Otherwise the page is in good shape - schema panel, klein caveat on the control, flagged-menu pricing on the button, esc() on every library-derived string. Six smaller defects around the estimate/start/poll/control seams, all with the same shape: the page trusts the happy path of a route that has a refusal.

## Bugs & vulnerabilities

**[MEDIUM] Regenerate mid-run replaces the running job: its Pause/Cancel/progress vanish while it keeps spending, and the old poll interval leaks** - `rgStart` lines 546-557
- What: the flagged badge appears DURING a run as soon as a floor failure lands (`flagged_count` rides every poll). Opening it and pressing Regenerate sets `JOB=r.job_id` and `poll=setInterval(...)` without clearing the running interval: the page now shows only the regen job; the library job runs on (Replicate spend continues) with no Pause/Cancel reachable and no progress row; the first interval fires every 2 s for the rest of the session (after the regen job's `clearInterval(poll)` clears only the newer id).
- Trigger: a flagged image during a run + Regenerate (reachable; the server's registry allows concurrent jobs).
- Impact: uncontrollable spend on a job the page no longer shows (G19 class); an interval leak.
- Fix: refuse Regenerate while a job is in flight (`JOB && go.disabled`) with a plain message; `clearInterval(poll)` before re-arming. Battery `LIB_regen_guards_running_job_and_interval` RED->GREEN.
- Verification: CONFIRMED (traced through `check()`'s `JOB` global and `libgen_regen`'s registry insert).

**[LOW] A refused estimate renders "undefined images · $undefined" and leaves Generate ENABLED** - `estimate()` lines 400-410
- What: `libgen_estimate` answers `{error}` with 400 (unpriced model, MODEL-SWEEP) or 500 (`build_plan` raising - the library_gen fork's out-of-unit note); the page has no error branch: `${e.images}` etc. render `undefined`, the funding warning says "Ensure ≥ $undefined", and `go.disabled = (undefined===0)` = false - Generate lit with no price on it (G19/R7). A network failure throws out of the handler and leaves the previous estimate on screen for a changed selection.
- Fix: error branch (message in the est row, Generate disabled) + try/catch. Battery `LIB_estimate_error_locks_generate` RED->GREEN (server evidence: 400 `{error}` for an unpriced model).
- Verification: CONFIRMED.

**[LOW] A double-click on Generate starts two paid jobs** - `start()` lines 411-424
- What: `go` is disabled only after the server answers; the Studio page disables before its fetch. Two clicks inside the round trip = two `libgen_start` calls = two jobs, the second's id overwrites `JOB` (the first becomes the orphan class above).
- Fix: disable at entry, re-enable on error, clear the interval. Battery `LIB_start_disables_before_fetch` RED->GREEN.
- Verification: CONFIRMED.

**[LOW] `ctrl()` swallows the server's refusal - the 409 on Resume never reaches the user** - lines 558-562
- What: `libgen_control` answers 409 `{error:"job thread still running - pause takes effect between images; try again shortly"}` when Resume is pressed while the worker is still alive; the page ignores the response. Resume looks dead (G20 error-path honesty). Also `if(action==='resume'&&!poll)` never re-arms because `poll` is never nulled after a clearInterval.
- Fix: read the response, alert `r.error`; always re-arm the interval on resume. Battery `LIB_ctrl_surfaces_server_refusal` RED->GREEN (server evidence: 409 reproduced with a live thread in `_LIBJOBS`).
- Verification: CONFIRMED.

**[LOW] `check()` has no exit for a vanished job - a 404 polls forever with "undefined/undefined done"** - lines 425-444
- What: after an app restart (in-memory `_LIBJOBS` empty) the poll answers 404 `{error}`; `j.status` is undefined so neither the done nor the cancelled branch clears the interval; the bar reads `undefined/undefined`, `$0.000 spent`, Generate stays disabled.
- Fix: a `!j.status` branch that clears the interval, says the job vanished and points at the library folder; a fetch throw waits for the next tick. Battery `LIB_poll_ends_on_missing_job` RED->GREEN.
- Verification: CONFIRMED (poll 404 traced).

**[LOW] Two static note rows (R1)** - lines 130, 176
- What: the wildness explainer ("0% = familiar subjects…") and "One generation per selected file — the price shown is the whole spend" are static informational rows; the bible puts information in tooltips (the same page already does that for Shape/Variation/Colour hints).
- Fix: the wildness text becomes the slider row's title; the regeneration text becomes the Regenerate button's title (its own tooltip text merged). Battery `LIB_no_static_note_rows` RED->GREEN. A change to a design surface: G24 asks for a real capture before it is called done - the lead's call.
- Verification: CONFIRMED (bible R1 text).

**[LOW] The pricebar ships hardcoded per-image prices; with no priced catalog rows the emptied select sits beside the literal "$0.025 / image"** - line 217, `boot()` 226-231
- What: `boot()` empties the select and refills it from priced rows but updates `priceval` only when options exist - the stale literal stays. Same UI-1 claim as the Studio page.
- Fix: empty select + "—" placeholder, hide the row when nothing is priced. Battery `LIB_pricebar_has_no_stale_literals` RED->GREEN.
- Verification: CONFIRMED.

## Missing safeguards
- The packs grid renders `p.id` / `p.name` / `t.name` from the shipped catalog via innerHTML unescaped - our own data today; `esc()` would cost nothing.
- `openLibFolder` shows `r.error` through `alert` - fine; `rgStart`'s `alert(r.error)` too.
- No cancel-confirm on a running job's Cancel (a mis-click stops a paid run; the run's paid images are kept, so recoverable).
- `estimate()` is called on every keystroke of every count field with no debounce - correct, chatty.

## Adversarial verification pass (refuted claims)
- "Origin/CSRF: `openLibFolder` and `vaultDoLock`-style bodyless POSTs lack Origin" - refuted: same-origin POSTs carry Origin in every engine including WebView2; `_origin_guard` admits local origins.
- "`e.thumb` / `e.reason` in the flagged list are injectable" - refuted: thumb is a server data URI in a src attribute; reason goes through `esc()`.
- "`ms.value=CAT.defaults.model` can select a model missing from the priced list" - refuted: a missing value leaves the select on its first option; the catalog default is priced.
- "`selection()` sends `count:NaN` for a blank per-pack override" - refuted: `ov?parseInt(ov):def` - blank falls to the global default.
- "The klein caveat is a selection-fired note row (R1)" - refuted: it rides the option label + title (LIB-KLEIN-WARN), no row.
- "`check()` on status 'error' keeps polling forever" - refuted: 'error' is the paused-with-Resume state by design (`pause_reason` shown, Resume offered); the server holds the job for resume.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `74d03b2a6c8de4ea473bb0c145929855dcaaa9fb129036389cf2c889d606deec`. Rows AF-LIB-REGEN-MIDRUN, AF-LIB-ESTIMATE-REFUSED, AF-LIB-DOUBLE-START, AF-LIB-CTRL-RESPONSE, AF-LIB-POLL-EXIT, AF-LIB-NOTE-ROWS, AF-LIB-PRICEBAR-LITERALS in `docs/remediation_manifest.json`, same commit.

