# Colibri bug review — tools/ui-harness.mjs

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: 126777bc4baff11491e05e12fa3bb629390213651a38d2af8dc623f0cbf2b2f2
NOTE (consolidator, 2026-09-03): the F1 manifest gap was independently re-verified — `film-adversary` and `sound-plate` rows exist in docs/FEATURES.md (lines 101-102), zero matches for either id in tools/*.mjs (jcodemunch citable absence), and line 1514 `process.exit(fail || missingTests.length || missingRows.length ? 1 : 0)`.

### Meta
- path: tools/ui-harness.mjs | sha8: 126777bc | lines: 1514 | context-pack: last touched in 8a38bc3 (runs-manager/recycle-delete wave); manifest gap source rows landed in e333931 (2026-08-27)

### Review

## Verdict
**FAIL — ship-blocking defects.** The harness's own manifest contract is permanently broken: `npm run test:ui` cannot exit 0 on this machine because two shipped features (`film-adversary`, `sound-plate`) have manifest rows but no registry tests — simulated with the file's exact regex, `missingTests = ['film-adversary', 'sound-plate']` on every run. Beyond that: one test silently rewrites the owner's persisted film defaults, one test has two genuinely vacuous pass paths, and the `--only` documented invocation form does not parse. Accounting and per-test isolation are otherwise sound (a thrown check fails only its row, screenshots captured, exit code counts fail + both gap directions), and selector spot-checks against `src/` mostly held up (the `SCORE engine` aria-label is template-generated and does exist at runtime — verified `SettingsConsole.tsx:169`).

## Bugs & vulnerabilities

**[HIGH] Permanent MANIFEST GAP: `film-adversary` and `sound-plate` have no harness tests — every run exits 1** - `line 1478` (detector), `lines 159–1475` (registry) — CONFIRMED
What: docs/FEATURES.md (rows added in commit e333931, 2026-08-27) declares 56 feature ids; the REGISTRY holds 54. Running the file's own gap computation verbatim: `missingTests: ['film-adversary', 'sound-plate']`, `missingRows: []`.
Trigger: any `npm run test:ui` (any tier, including `--only`).
Impact: the fast tier can never be green. Per AGENTS.md ("keep it green", harness before commits), a permanently-red gate either blocks every commit or trains the operator to ignore exit code 1 — after which real failures hide in the noise. The two features themselves (the storyboard adversary, the sound plate / DocView) violate the "manifest row AND a harness test" rule.
Fix: add registry rows for both ids (e.g., sound-plate: open an audio artifact from the library, assert the waveform plate + `audio-placeholder`; film-adversary: a fixture record at THE PLAN shows the ADVERSARY verdict line), or fold their checks into existing rows under those ids.

**[HIGH] `film-defaults` rewrites the owner's persisted film defaults and never restores them** - `lines 1091–1098` — CONFIRMED
What: `page.select('select[aria-label="Film quality"]', "balanced")` and the SCORE-engine select both fire the real `save()` handler (SettingsConsole.tsx:155–160 → `setFilmDefaults` → the gitignored server-side store). The test verifies persistence across reload and closes settings — no restore of the previous quality/score values.
Trigger: every fast-tier run.
Impact: the machine's standing film orders are silently mutated — quality flips to balanced and `engines.score` is pinned from AUTO to the first catalog engine; subsequent real films are priced and shot with different defaults than the owner chose. This contradicts the file's own discipline (library tests seed and delete fixtures in `finally` blocks).
Fix: read the two values before touching them (`getFilmDefaults` via `/api/...`) and restore in a `finally`, or assert read-only (open settings, verify renders, don't select).

**[HIGH] `library-window` has two silent-pass paths — the check cannot fail when its precondition yields zero** - `lines 429` (`if (filmCells > 0)`) and `lines 444` (`if (hasOpen)`), seed swallowed at `line 401` — CONFIRMED
What: the click-selects contract (amber edge, foot count) runs only `if (filmCells > 0)` and the z-order contract only `if (hasOpen)`; when `.lib-cell .lib-thumb` or `.lib-open` match nothing the blocks are skipped and the row still prints PASS. The fixture seed that guarantees cells exist is `await fetch(...fixture...).catch(() => {})` — its failure is swallowed, so on the documented stale-preview trap (a build predating `/api/library/fixture`) or on class rename (selector drift), the gesture-grammar and z-order features report green while broken.
Trigger: selector drift, stale preview serving :4173, or fixture-route failure.
Impact: exactly the vacuous-check class the design adversary banned ("assertions that can't fail: selectors matching nothing treated as pass"). Sibling tests do this honestly (`return skip(...)` at lines 319, 342, 637, 658).
Fix: count cells/open-keys once, and if zero `return skip("no cells/open keys — fixture failed to seed")` instead of silently passing.

**[MEDIUM] Documented `--only boot,nav-surfaces` form does not parse — runs the whole fast tier; unknown id runs zero tests and exits 0** - `lines 8` (usage) vs `line 18` (`a.startsWith("--only=")`) — CONFIRMED
What: the parser only accepts `--only=`. `node tools/ui-harness.mjs --only film-wizard` (the documented form, and the form `npm run test:ui -- --only film-wizard` produces) leaves `only = []` → the `only.length` guard at line 1484 falls through → every fast test runs. Separately, `--only=typo-id` selects zero tests; with pass=fail=0 the exit code is 0 (today masked only by the permanent manifest gap — after fixing that, a typo'd run is silently green).
Trigger: following the file's own usage comment.
Impact: minutes-long unintended full runs; worse, after F1 is fixed, a typo'd `--only` yields a green exit with zero coverage.
Fix: accept the space form (`--only` followed by the list) and hard-error when an `--only` id matches no registry entry (`if (only.length && !selected.length) { console.error(...); process.exit(1) }`). Neither change breaks the `test:ui` script.

**[MEDIUM] `gotoApp` hard-requires `button[title="Switch bundle"]` — the entire harness bricks under the cloud-only profile** - `lines 103, 108` vs `DeckControls.tsx:242,284` — CONFIRMED (latent)
What: under the supported `cloud-only` profile the deck's LOCAL arm renders "This Caliper runs CLOUD-ONLY…" instead of the BundlePicker, so `localArrived` is false, the reload at 106 doesn't help, and `waitForSelector('button[title="Switch bundle"]', 15000)` throws — for every single test, since `gotoApp` gates the runner loop (line 1495).
Trigger: flipping the machine to the cloud-only profile (SETTINGS · MODEL ROUTES) and running the harness.
Impact: total harness failure unrelated to any feature regression. Latent today (local GPU profile).
Fix: wait for either the bundle button or the cloud-only note (`button[title="Switch bundle"], .deck-cloudonly-note`-equivalent) and let LOCAL-arm tests skip honestly under that profile.

**[MEDIUM] `library-window`'s film-key finder is index juggling that false-fails with 0 or 1 films** - `lines 414–421` — CONFIRMED (logic traced against ScreenStage.tsx rail markup)
What: the rail renders `FILMS` heading then film keys, so `findIndex(x => x.previousElementSibling…includes("FILMS"))` returns 0 and `keys.find(k => keys.indexOf(k) > 0)` clicks the SECOND film key. With exactly one film it clicks `ALL ONE-OFFS` instead → meta equals "ALL ONE-OFFS" → false FAIL "a film key did not scope the window". With zero films the test fails earlier at the FILMS rail check (line 408) instead of skipping.
Trigger: any machine (or profile state) with <2 films.
Impact: fresh-install false failures presented as feature regressions; the "pick a film key" step is also arbitrary (second film rather than a named one).
Fix: click the first `.lib-rail-key` whose `previousElementSibling` is the FILMS heading (i.e. the element findIndex already located), and `return skip(...)` when `films` is empty.

**[MEDIUM] `film-runview` converts wizard-navigation breakage into a SKIP and never asserts the manifest's stated contract** - `lines 757–760` — CONFIRMED weak / PLAUSIBLE masking
What: five NEXT presses are optional-chained with no per-click assertion; then any absence of `/THE FILM|priced/` returns `skip("the wizard opened a fresh draft…")` even though line 747 already established a finished run exists. The manifest row (`film-runview`) promises "A finished run shows the grade rail and WATCH" — WATCH (FilmWizard.tsx:1376) and the grade rail are never asserted anywhere.
Trigger: a regression in the wizard's NEXT keys or the run block makes this row report SKIP (exit code 0) instead of FAIL.
Impact: the run-view feature — a core surface — has effectively no failing assertion; its coverage is a skip-shaped vacuous pass.
Fix: after the walk, distinguish "no run record" (skip) from "wizard did not advance" (fail — assert the rail landed on THE BILL/THE RUN), and assert at least the WATCH key and legend line for the `done` run.

**[MEDIUM] `buttonExists` is a misnomer that reduces `queue-surface` to a body-text check** - `lines 61, 732–734` — CONFIRMED
What: `buttonExists` tests `document.body.innerText`, not the presence of any button. `queue-surface`'s only assertion is therefore "the text 'clear queue' appears somewhere" (it does, QueueSurface.tsx:152); the "Server tasks" check is an `if` that only console.logs. The manifest row promises "Queue shows server tasks in detail and can clear".
Trigger: the clear-queue control disappearing while its label text survives anywhere (tooltip, help copy) → still passes.
Impact: thin but real false-pass surface on one of the five primary surfaces; the helper's name will mislead future test authors.
Fix: make `buttonExists` query buttons (like `clickButton`), and assert the "Server tasks" section heading (QueueSurface.tsx:90) rather than logging it.

**[LOW] `servedBundles` ignores `APP_URL`** - `line 156` — CONFIRMED
The precheck honors `APP_URL` (line 16) but ground-truth bundles are fetched from hardcoded `http://localhost:4173/api/bundles`; with `APP_URL` overridden to a live origin and 4173 down, this top-level await rejects and the process dies on a stack trace instead of a clean message. Loud, no false results. Fix: `fetch(`${APP}api/bundles`)`.

**[LOW] Fixture dirs are written before `try{}` — early throws leak `films/harness-*` records that can claim the wizard's front door** - `film-checkpoint` lines 1116–1129 (try starts 1130), `film-kf-review` lines 1209–1221 (try starts 1224) — CONFIRMED
A corrupt source `films/mv-user-song-mtd03326/autopilot.json` (`JSON.parse` throw) or a record without `storyboard.shots` (TypeError at line 1220) escapes before the `finally` cleans up, leaving a `createdAt: now`, `step: "producing"` record that wins the wizard resume on later runs (mitigated only by the START OVER fallbacks in the film tests). Fix: move the read/mutate/write inside the `try`, or mkdir last.

**[LOW] `--only` bypasses the render-tier ComfyUI precheck** - `lines 31, 1483–1488` — CONFIRMED
`--only=render-queue-done` runs a render test without `--renders`, so the :8188 precheck never fires; the test then fails at runtime with a less actionable error. Loud. Fix: when any selected test has tier "render", require the 8188 probe too.

**[LOW] `render-outputs-surface` hardcodes "Anima-Aesthetic" against a dynamic bundle pick** - `lines 1369 vs 1397` — CONFIRMED
The bundle is chosen dynamically (first `kind: "image`"), but the Outputs assertion greps for the literal name. If bundles.json is ever reordered/renamed, the test false-fails. Fix: assert `anima.name` appears.

## Missing safeguards
- No rejection of unknown `--only` ids (zero-test green run — see finding 4).
- No films-count guard in `library-window` (should skip honestly on a film-less machine, as `screen-reload-restore` and `outputs-archive` do).
- `nav-surfaces` asserts surface markers for plates 1, 2, 4 only — plates 3 and 5 are verified solely by `aria-pressed`, weaker than the manifest's "the surface heading changes" (line 165).
- `vram-instrument` asserts only "some GB text exists"; the manifest row also promises the resident list — unasserted (line 1365).
- `cleanLibraryFixtures` removes leftover fixture *records* but not the 296 stale `films/library-fixture-*` dirs from the pre-2026-08-27 fixture route still on this machine's disk — a one-time sweep (or extending the cleanup to those dirs) would keep `films/` truthful.
- `optimizer-cloud-brain` spends real cents on every fast-tier run when a key is stored (line 1438) — deliberate per comments, but there is no env opt-out for offline/CI-style runs.
