<!-- source: src/components/FilmWizard.test.tsx | reviewer: glm-5.3-zai-in-session | sha256: 0d5fc24b66dc00235f5f4f6f03dcb6d3f27601bced1345109a32239c2d879942 | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: TESTFILEHUNT - the first colibri bug hunt on TEST files (top 10 by guarded-module fan-out); fresh-context pass, no prior bug review existed. The HIGH re-verified first-hand by the orchestrator (persistence effect FilmWizard.tsx:723-729 + auto-resume :688-706 + the optional-chained clickScenario helper). -->

## Verdict (1-2 sentences)
The suite's core claims (draft burial/survival, attention-chip navigation, arm consumption) are real and regression-sensitive — I traced each to production code and they would fail on the bugs they name. But one contamination runs on every green run: test 121's walk leaks a localStorage draft that test 135 unknowingly inherits, silently voiding 135's scenario-click act, and the beforeEach's reset contract covers only 3 of the API mocks and never localStorage.

## Bugs & vulnerabilities (worst first)

**[HIGH] Test 121 leaks the wizard draft; test 135's scenario act silently no-ops on the residue - `line 126` / `line 137` (victim at 135-143)**
What: Test 121 removes the draft at start (line 126) but its walk (`clickScenario` at 128) sets `draft.pending`, and the persistence effect (FilmWizard.tsx:723-729) writes `caliper.wizard-draft` to localStorage; unmount clears nothing (the removeItem only fires on a pending→null transition while mounted). Test 121 never removes it at end — unlike every other writing test (163, 191, 257, 291). Test 135 takes no start-cleanup, so its mount hits the AUTO-RESUME branch (FilmWizard.tsx:691-705): the leaked draft resumes at stepIdx 1, the scenario picker never renders, and `clickScenario` (test line 63, optional-chained `?.click()`) silently no-ops before `NEXT` moves 1→2.
Trigger: Every green run, in file order 121 → 135 (vitest runs tests sequentially in declaration order).
Impact: Test 135's described flow ("mount, pick MUSIC VIDEO + USER SONG, NEXT") is a fiction — it exercises the auto-resume of the previous test's leftover, not the picker. Its assertions pass only because the leak happens to be an `mv-user-song` draft with the same default shape; a `chooseScenario` regression is invisible to this test (only 103 would catch it), and any reordering or shape change in 121 flips 135 red or, worse, keeps it green through a different path than the one named. This is exactly the commissioned class 2/4 pair: a vacuous act plus state leakage — and it is active, not failure-conditional.
Fix: Add `localStorage.removeItem("caliper.wizard-draft")` to the beforeEach (after the film-store reset at line 79), and have test 121 clean up after itself like its siblings. Additionally make `clickScenario`/`clickText` throw when the target button is missing so a vacuous act can never pass silently.

**[MEDIUM] beforeEach resets only 3 of the mocked APIs - the `autopilotDraftStream` override from test 294 persists into all later tests - `line 81` vs `line 309`**
What: The beforeEach (lines 80-85) resets `autopilotList`, `autopilotStatus`, `getKeys` only, with the comment "the api mocks back to their defaults" (lines 76-78). Test 294 installs `vi.mocked(autopilotDraftStream).mockImplementation(...)` — a promise that never resolves until `finishDraft` is called. No later reset exists (`getFilmDefaults`, `filmLadder`, `autopilotCreate`, `autopilotPatch`, `autopilotBill` are likewise never reset, though never overridden today).
Trigger: Currently latent — test 332 (the only test after 294) never presses DRAFT. It activates the moment any future test that drafts is appended after line 330.
Impact: That future test hangs on an unrelated test's stub, pointing the author at the wrong code. The stated hygiene contract in the beforeEach comment is false.
Fix: In beforeEach, reset and re-default every mock the file overrides (at minimum add `autopilotDraftStream` back to its factory implementation).

**[LOW] Test 145's name promises "a reopen resumes the server record, never a twin" - no reopen and no twin check exist - `line 145`**
What: The test verifies localStorage retirement and record adoption ("Night Drive", lines 160-161) but never reopens the wizard and never re-presses DRAFT to prove a second record isn't minted — the twin protection (`ensureRecord`'s `if (draft.record) return draft.record`, FilmWizard.tsx:897-899) is unguarded.
Trigger: A regression where the commit point creates a second record (e.g., ensureRecord ignoring the adopted record).
Impact: The named bug ships while the test stays green; the name over-promises (class 5).
Fix: After adoption, click DRAFT again and assert `autopilotCreate` was called exactly once.

**[LOW] Test 88 asserts the Settings invitation exists but never its promised action - `line 98`**
What: "a Settings invitation" is pinned only as the string "SETTINGS" (matched by the "OPEN SETTINGS" button, FilmWizard.tsx:1085). The click path — `onClose()` plus `setSettingsOpen(true)` — is never fired or asserted (class 5/10: the button's visible result is untested, against the repo's own "every button press must produce a visible result" rule).
Trigger: The gate button stops opening Settings (e.g., handler dropped).
Impact: The gate still "passes" while its one remedy is dead glass.
Fix: Click OPEN SETTINGS and assert `useUiStore.getState().settingsOpen === true` (and the onClose spy fired).

## Missing safeguards (bullets)
- Zero coverage of commit c001de9's changed lines: the canonicalized window keys `film:<id>::<file>` at the upscale (FilmWizard.tsx:635) and WATCH (:1760) sites. Class 7 finds no rot only because no fixture exists — a `:`→`::` regression there ships silently. These paths need a done-step test asserting the `openAsset` key.
- The "clicking around is free" half of the commit-point rule (no server write before DRAFT) is only incidentally pinned via pane text in test 121; no test asserts `autopilotCreate` was not called during a walk.
- All settling is timing-based: the fixed 30ms sleep in `mount` (line 50), microtask-count flushes (`await Promise.resolve()` ×2 at 178/205/213/275/282), and 10-15ms sleeps for the real `setTimeout(0)` re-persists (250, 285). The bury test's door-standing assertion additionally rests on the StrictMode two-pass refresh generations resolving in FIFO microtask order (FilmWizard.tsx:651/680 + filmRunsStore `derivePin` generation guard) — deterministic today, but nothing in the test awaits the chip before asserting; a new mount effect could reorder it. A waitFor-style condition helper would remove the whole class.
- Test 220's "a later plain open stands at the door again (LIST FIRST)" claim (lines 233-235) is only implied by `pendingResumeId === null`; no second mount ever demonstrates the door stands.
- The chip's one guard — `disabled` while a song uploads (FilmWizard.tsx:1813) — is untested, despite test 194's name being about the chip never being greyed out.
- `clickText`/`clickScenario` use optional chaining, so a missing button is indistinguishable from a successful act until (and unless) a later assertion happens to fail.

context-pack: FilmWizard.test.tsx (full, current on-disk), FilmWizard.tsx lines 1-1847 (effects at 651/669/680/723, auto-resume 691-718, ensureRecord 897-927, resumeRun 933-986, chip/footer 1801-1841), filmRunsStore.ts (derivePin/takeResume/reset), uiStore.ts, vitest.setup.ts (localStorage + scrollIntoView shims), git log for both files, and the c001de9 diff confirming the `film:<id>::<file>` key change at the upscale/WATCH sites.
new-findings: 4
