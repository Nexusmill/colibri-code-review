# Test-file bug hunt synthesis (2026-09-17) — TESTFILEHUNT

Owner commission: "it seems to me that we should absolutely bug hunt test
files, that makes sense. just for giggles do a bug hunt on the top 10
test files. and lets see what happens." The first colibri bug hunt ever
aimed at TEST files (the count doctrine had explicitly noted tests were
never targeted). Board = top 10 of the 60 vitest test files by
GUARDED-MODULE FAN-OUT (how many distinct repo source modules the test
imports - tests are import-leaves, so import PageRank cannot order them;
fan-out measures how much code each test guards), size as tiebreak. The
lens: a defect in a test is a LIE ABOUT PROTECTION - assertions that
cannot fail, vacuous acts, tests pinning wrong behavior, state leakage,
timing races, fixture rot. Ten fresh-context subagents (glm, in-session);
Phase 3 verification ran per finding inside each hunt, and all three
HIGHs plus the one production-side lead were independently re-verified
against current bytes by the orchestrator (the FirstRun seeded-mode
tautology read first-hand at lines 87/265-266; the FilmWizard draft-leak
mechanism traced through the persistence effect FilmWizard.tsx:723-729,
the auto-resume branch :688-706, and the optional-chained clickScenario
helper; the FilmRuns pre-sorted fixture read directly at lines 59-77;
the SettingsConsole keyedServices identity lead confirmed at
SettingsConsole.tsx:308 + :346). Reviews only - NOTHING is remediated
from this hunt without the owner's pick.

## The board

| # | File | Pass | New | Worst |
|---|------|------|-----|-------|
| 1 | src/surfaces/OutputsSurface.test.tsx | fresh | 4 | MEDIUM — the name promises kind·day grouping; no grouping assertion exists anywhere in the file |
| 2 | src/stores/stores.test.ts | fresh | 5 | MEDIUM — a duplicate-id fixture makes the "reselects the first remaining" test exercise the id-carry branch instead of the named fallback |
| 3 | src/components/FirstRun.test.tsx | fresh | 5 | HIGH — "seats the deck LOCAL" asserts the value its own beforeEach seeded; the click's effect is unguarded |
| 4 | src/components/SettingsConsole.test.tsx | lineage _r2 | 4 | MEDIUM — preset restore/delete assert the API verb but never the promised UI outcome (chip gone, table refreshed); the armed-face assertions are tautologies by construction |
| 5 | src/surfaces/GenerateSurface.test.tsx | fresh | 3 | MEDIUM — the "component readout" assertion only reads text inside a COLLAPSED details element; nothing visible is guarded |
| 6 | src/components/CommandPalette.test.tsx | fresh | 1 | LOW — the palette's Enter fires an unawaited VRAM-check fetch chain that survives the test |
| 7 | src/components/FilmWizard.test.tsx | fresh | 4 | HIGH — test 121 leaks a localStorage draft that test 135's mount AUTO-RESUMES, silently voiding its scenario click - active on every green run, not failure-conditional |
| 8 | src/components/FilmRuns.test.tsx | fresh | 5 | HIGH — "pinned FIRST" cannot fail: the fixture already lists the needy run at index 0, so the pin reorder is unguarded |
| 9 | src/components/DocView.test.tsx | lineage _r2 | 5 | MEDIUM — "their own COPY key" unprovable with a single code block; an unguarded indexOf anchor lets the last-panel no-join negative pass vacuously |
| 10 | src/surfaces/bundle-io.test.tsx | fresh | 6 | MEDIUM — "keeps its own id" never touches an id (the collision-blanking path is dark); test 1's URL "stub" permanently mutates the global URL constructor |

**Totals: 42 findings — 0 CRITICAL / 3 HIGH / 19 MEDIUM / 20 LOW.**
One production-side defect surfaced from a test's missing safeguards
(recorded below, routed to a component board - it is NOT a test finding).

## What the test-hunt lens found (the cross-file shapes)

1. **The lie-by-construction trio (all three HIGHs).** A test asserts a
   value it (or its fixture) already arranged: FirstRun's beforeEach
   seeds `mode: "local"` and the test asserts `mode === "local"` after
   the click; FilmRuns' fixture pre-sorts the needy run to index 0 so the
   pin-reorder cannot fail; FilmWizard's leaked draft makes the next
   test's scenario click optional-chain into silence while the
   assertions still pass. In every case the named protection can regress
   with the suite green - the exact catastrophe a test exists to prevent.
2. **No afterEach discipline anywhere on the board.** Every file cleans
   up inline AFTER its assertions (skipped on any failure) or not at
   all; `unstubGlobals` is absent from the vitest config, so a failed
   assertion leaks that test's fetch stub into every later test
   (flagged in stores, OutputsSurface, SettingsConsole, bundle-io,
   GenerateSurface, FilmRuns, DocView). The FilmWizard leak is the only
   one ACTIVE today; the rest are failure-conditional cascades.
3. **Timing-based synchronization everywhere.** Fixed sleeps (25-30ms)
   and hand-counted microtask ticks (`await Promise.resolve()` x2-3)
   race five-deep async chains in FilmWizard, FilmRuns, SettingsConsole,
   bundle-io; each is deterministic today only by FIFO-microtask
   accident, and one added `.then` anywhere in production flips them
   into false alarms that point at the wrong code. A waitFor-style poll
   helper would delete the whole class.
4. **Names that promise more than the assertions deliver** (the
   recurring MEDIUM): kind·day grouping unasserted, the hydrate
   once-per-record guard unexercisable, "and closes" with onClose never
   spied, "never a twin" with no second DRAFT press, "component
   readout" reading collapsed DOM, "self-describing envelope" never fed
   back through validateBundles, the clearAll body never checked,
   "directs to Generate" pinning directionless copy.
5. **Fresh production code landed without its surface tests.**
   Yesterday's c001de9 lines - the canonicalized `film:<id>::<file>`
   window keys and FilmRuns' closeByPrefix wiring - have zero coverage
   in the wizard/runs suites (the store has a unit test; the component
   wiring does not), and FirstRun's new comfyPortNow derivation is
   satisfied only by the unresolved module default (a revert of
   yesterday's fix stays green).
6. **Fixture rot is rare but real**: stores' duplicate-id bundle
   fixture (a state validateBundles rejects), DocView's handcrafted DOC
   still using the retired single-line anchor form, FilmRuns' mock
   shapes cast `as never` so tsc cannot catch drift, bundle-io's
   hardcoded factory-catalog length.

## Ranked: what deserves fixing first (if the owner picks remediation)

1. **[HIGH] FilmWizard draft leak** — the only ACTIVE lie: test 135
   guards nothing today. beforeEach draft-removal + helpers that throw
   on a missing button.
2. **[HIGH] FilmRuns pinned-first fixture** — flip the fixture so the
   needy run is NOT index 0; the surface's headline contract is
   currently unguarded (and production's newest-first listing makes the
   non-index-0 case the COMMON one).
3. **[HIGH] FirstRun seeded-mode tautology** — seed `mode: "cloud"` so
   the click is the only path to the asserted value.
4. **The afterEach wave** — one `afterEach` per file (store resets,
   unstubAllGlobals, host removal) + `unstubGlobals: true` in the
   vitest config; kills every failure-conditional cascade on the board
   in one sweep.
5. **The three name-vs-assertion MEDIUMs with real contracts behind
   them** (bundle-io's id/collision darkness, SettingsConsole's preset
   outcome assertions, stores' branch-swapped reselect fixture).
6. **The waitFor helper** — a small poll-until predicate util adopted by
   the five timing-based files; structural sync instead of ticks.
7. The LOW tail (anchored regexes, unawaited unmounts, count-body
   checks) — cheap, per-artifact fixes.

## Production-side lead (NOT a test finding - routed for a component board)

SettingsConsole.tsx:308 passes `keyedServices={new Set(...)}` - a fresh
Set identity on every render - into FilmDefaultsSection, whose catalog
effect depends on `[keyedServices]` (SettingsConsole.tsx:346): the
getFilmDefaults + per-leg getCloudModels fetch chain re-runs on EVERY
parent re-render (every keystroke, every status line, every TEST
verdict). CONFIRMED by the orchestrator against current bytes. The test
suite hides it structurally (the api/film factory mock makes fetch
identity invisible). Recommend it joins the next source-file board or a
targeted fix wave.

## Doctrine notes (first run of the test-file lens)

The lens works: all ten files yielded material, three of them HIGHs,
and 42 findings landed where the source-file boards (30 files, 49
findings) average ~5/file - comparable yield on files everyone assumes
are "just tests." The dominant classes have NO source-file equivalent
(tautology-by-seed, vacuous act via leaked state, name-overpromise), so
test files earn their own board series going forward. Two lineage
passes (SettingsConsole, DocView at identical shas) both paid: the
prior SettingsConsole review had OVERSTATED its own coverage ("armed
face text asserted" - the assertions cannot fail), a class the fresh
hunt caught only because the prior text was loaded as context. The
guarded-module fan-out ranking behaved: the top three files guard the
most store surface and produced the densest findings; the smallest file
on the board (CommandPalette, 38 lines, 1 test) produced the fewest -
the ranking and the yield agree.

Awaiting the owner's remediation pick; nothing is being fixed from this
hunt without it.
