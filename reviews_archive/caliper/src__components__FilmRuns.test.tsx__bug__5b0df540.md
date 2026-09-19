<!-- source: src/components/FilmRuns.test.tsx | reviewer: glm-5.3-zai-in-session | sha256: 5b0df5405979d33562d5c78987aec6954d403fd26af1c9b1ddf53b28a1233673 | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: TESTFILEHUNT - the first colibri bug hunt on TEST files (top 10 by guarded-module fan-out); fresh-context pass, no prior bug review existed. The HIGH re-verified first-hand by the orchestrator (fixture order read directly). -->

## Verdict

The suite's pin-derivation, two-press delete, and gate-round-2 coverage is real and passing (verified: `npx vitest run src/components/FilmRuns.test.tsx` → 9 passed), but three of its named promises are structurally unverifiable as written — the "pinned FIRST" order check is satisfied by the fixture's own sort order, the gate-r4 section asserts the wrong store field, and yesterday's `closeByPrefix` delete wiring (c001de9) landed with zero integration coverage and an unmocked, unreset real screenStore running under the test.

## Bugs & vulnerabilities

**[HIGH] "Pinned FIRST" cannot fail — the fixture pre-sorts the needy run to index 0** - `line 59` (fixture) / `line 77` (assertion)
What: The test name (line 56) and comment promise the needy run "PINS at the top". The runs fixture lists `mv-generated-aaaa` (the needy run) FIRST already; `expect(rows[0]).toContain("PLAN READY TO APPROVE")` passes whether or not the pin-reorder (`FilmRuns.tsx:104-107`, `[runs.find(needsYou), ...runs.filter(...)]`) runs at all.
Trigger: Any regression that drops the reorder (rows rendered in raw list order while the pin marker stays on the row) — e.g. someone renders `runs` directly.
Impact: In production the server lists newest-first, so a needy older draft is frequently NOT index 0 — exactly the case the reorder exists for. The surface's headline contract ("the needy run rides the top") is unguarded; line 75 only proves the marker exists, not its position. CONFIRMED (fixture order read directly; no other test has a multi-row list where the needy run is not first).

**[MEDIUM] Gate-r4 section asserts `resumeArmed` — the r4 regression mutates `wizardReturnId`, which is never checked** - `line 232`
What: The comment (lines 223-226) promises "the trip dies at the WIZARD, not at this window's unmount (StrictMode's mount cycle would wipe the id... gate r4)". The scenario (set return id → unmount) is exactly the r4 cleanup path, but the assertion is `expect(resumeArmed).toBe(false)`. `setWizardReturnId` never touches `resumeArmed` (filmRunsStore.ts:81), and the component cleanup (FilmRuns.tsx:33-40) only guards `wizardReturnId`.
Trigger: Re-adding `setWizardReturnId(null)` in the effect cleanup — the precise r4 bug.
Impact: Test stays green; the wizard's YOUR RUNS return-trip silently breaks. CONFIRMED (traced both store fields; `resumeArmed` was false before mount and nothing in the path sets it).

**[MEDIUM] Yesterday's `closeByPrefix` delete contract is unguarded, and the real screenStore runs unmocked and unreset** - `lines 46-54, 171-206`
What: Commit c001de9 added `useScreenStore.getState().closeByPrefix(`film:${id}:`)` to `confirmDelete` (FilmRuns.tsx:76) after this file's last touch (108628d). The DELETE tests never mock screenStore, never reset it in `beforeEach`, and never assert the call — with empty windows `closeByPrefix` early-returns (screenStore.ts:174-175), so the suite passes blind. The store has unit coverage (stores.test.ts:445) but the component→store wiring is what a refactor deletes.
Trigger: Removing the `closeByPrefix` call from FilmRuns.tsx, or any future test seeding screen windows — zustand persist (`caliper.screen`) then carries state across tests in this file.
Impact: The BUGHUNT12 zombie-window guard's wiring regression ships silently; latent cross-test leakage (class 7 + class 4). CONFIRMED (component/store diff traced; live run green proves no assertion touches it).

**[MEDIUM] Hand-counted two-tick microtask flush races a five-deep async chain** - `lines 200, 252`
What: After CONFIRM, the chain is `await autopilotDelete` → `await autopilotList` (inside refresh) → `await autopilotStatus` (inside derivePin) → derivePin resolution → refresh resolution → confirmDelete continuation ≈ 5 chained microtask continuations plus a re-render, flushed by `await Promise.resolve(); await Promise.resolve()` plus act's internal awaits — with no comment on why two, no `waitFor`/polling.
Trigger: One additional `await` anywhere in `confirmDelete`/`refresh`/`derivePin` (e.g. making the delete path await something new).
Impact: Line 204 ("Second Draft re-pins") and line 253 (`wizardReturnId` cleared) fail against correct production behavior — a false alarm that erodes trust in the delete contract's guard. Currently deterministic-pass (FIFO microtasks; verified run), so the defect is the unaudited margin, not a live flake. CONFIRMED as fragile-by-construction.

**[LOW] "Recycle Bin" assertion is satisfied by the ARM message alone** - `line 202`
What: `expect(host.textContent).toContain("Recycle Bin")` claims CONFIRM executed, but the DELETE arm click already sets `${name}: to the Recycle Bin - ...` (FilmRuns.tsx:144), so this assertion passes even if `confirmDelete` never completes.
Trigger: confirmDelete hangs or rejects before its `setStatus`.
Impact: The status-report assertion is redundant-weak (lines 201/204 do catch non-execution today); it just cannot carry the weight its comment gives it. CONFIRMED.

## Missing safeguards

- Focus refetch (adversary m3, FilmRuns.tsx:31): no test that a `window.focus` event re-reads the run list.
- List-error path: no test of `listError` → the RETRY invitation (adversary m2), nor confirmDelete's `(the run list could not refresh...)` suffix.
- Delete FAILURE path: no test of `autopilotDelete` rejecting → `statusError` + GOT IT, and — critically — that a failed delete does NOT clear `wizardReturnId` and does NOT refresh (FilmRuns.tsx:80-83, 90-92 ordering).
- `removed === false` branch ("already gone on disk", FilmRuns.tsx:77-78): untested.
- `openRun` clears `wizardReturnId` ("another run chosen", FilmRuns.tsx:47): asserted nowhere (test at line 140 checks arm + opens only).
- Single-arm invariant: DELETE on row A then row B (one row armed at a time) untested.
- The 30ms fixed sleep in `mount` (line 29) is a fixed-timer race by pattern; a polling/flush helper would also fix the line-200/252 fragility.
- Mock shapes are cast `as never` (lines 49, 50, 65, 68...) — fixtures can drift from `AutopilotRecord`/`AutopilotRunSummary` with tsc none the wiser; note `{ record: null }` is an unreachable real response (film.ts:207 rejects on null record).
- `mount()` never removes its host div from `document.body` (line 22-23) — body accumulates dead hosts across tests; benign while assertions are div-scoped.
- `beforeEach` resets filmRuns/ui partially but not screenStore or the `caliper.screen`/`caliper.ui` localStorage keys (only `caliper.wizard-draft` is removed).

context-pack: FilmRuns.tsx @ c001de9 + 108628d, src/stores/filmRunsStore.ts, src/stores/uiStore.ts, src/stores/screenStore.ts (closeByPrefix), src/api/film.ts (autopilotList/Delete/Status contracts), FilmWizard.tsx:233-274 (SCENARIOS/runFamily/runStageWords/NEEDS_YOU_*), vitest.setup.ts (localStorage shim), stores.test.ts:445 (closeByPrefix unit coverage), git log for both files, live vitest run (9 passed).
new-findings: 5
