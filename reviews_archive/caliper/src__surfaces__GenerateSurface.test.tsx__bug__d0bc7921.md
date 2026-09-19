<!-- source: src/surfaces/GenerateSurface.test.tsx | reviewer: glm-5.3-zai-in-session | sha256: d0bc7921502685c734747f58907fafcbd623e3702e95df98c348e15f3b2d6552 | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: TESTFILEHUNT - the first colibri bug hunt on TEST files (top 10 by guarded-module fan-out); fresh-context pass, no prior bug review existed. -->

## Verdict (1-2 sentences)
The file's four tests genuinely bind to production behavior (mutation-sensitive store/DOM assertions, all verified live-green against the current post-c001de9 code — no fixture rot), but one assertion claims a protection it does not deliver (a "component readout" that is only hidden DOM text), and both store resets are partial or misplaced, leaving latent cross-test leakage. The bigger exposure is omission: the Generate screen's namesake action — queueing — is never fired in this file.

## Bugs & vulnerabilities (worst first)

**[MEDIUM] "component readout" assertion only checks text inside the collapsed advanced `<details>` — it guards nothing visible** - `line 36`
What: The test name promises "renders bundle name, component readout, and the queue action", and line 36 asserts `host.textContent` contains "gemma.safetensors". That string renders only inside `AdvancedDrawer` (src/components/AdvancedDrawer.tsx lines 32-33), which sits inside `<details className="mt-2">` with no `open` attribute (src/surfaces/GenerateSurface.tsx line 175). `textContent` includes collapsed-details content, and jsdom applies no visibility filtering. The visible Generate pane has had no component readout since the deck redesign (705698f) — the readout the name remembers is gone, and the assertion quietly re-targeted the hidden drawer without renaming.
Trigger: Any regression that breaks or removes a visible component readout, or moves `AdvancedDrawer`/`text_encoders` wiring anywhere else in the mounted tree.
Impact: The test keeps passing while the promised user-visible protection is zero; a reader of the test list believes readout rendering is guarded.
Fix: Either rename the assertion's intent (assert the advanced drawer wiring) or assert visibility honestly — e.g. require the string inside an `open` details, or drop "component readout" from the test name and assert the drawer's summary text instead.
CONFIRMED (traced through GenerateSurface.tsx line 175 → AdvancedDrawer lines 32-33; `<details>` never opened in the test).

**[LOW] queueStore cleanup lives in the tail of test 4's body — skipped on any assertion failure, and no beforeEach/afterEach resets it** - `line 101`
What: `useQueueStore.setState({ jobs: [] })` runs only after all four assertions and the unmount succeed. `beforeEach` resets only `useBundlesStore`; `singleGuard`, `lastQueueError`, `queueRemaining`, and `socketState` are never reset anywhere in the file — tests 1-3 silently depend on module-creation defaults.
Trigger: Any assertion at lines 96-99 throwing, or any new test appended after test 4 (it inherits a leaked `jobs`/queue state unless the tail ran).
Impact: Latent ordering-dependent failures and false positives for future tests; today no in-file victim exists only because test 4 is last.
Fix: Move the reset to an `afterEach` (or reset the whole queue slice in `beforeEach`), not the test tail.
CONFIRMED (structure verified; live leak today: none — test 4 is the file's last test).

**[LOW] beforeEach's bundlesStore reset is partial — `paramEdits` (and `vramNote`/`vramPrompt`) leak across tests** - `line 20`
What: The `setState` at lines 20-24 replaces `params` wholesale but never resets `paramEdits`. Test 3's `setParam` writes `paramEdits["LTX-2.3-Distilled"].frames = 89` (bundlesStore.ts line 315-319), which persists into test 4 and into the persisted `caliper.bundles-ui` localStorage payload.
Trigger: A later test that calls `load()`/`save()` or reads `paramEdits` (both merge `paramEdits` over fresh defaults — bundlesStore.ts lines 159, 218).
Impact: Inert today (test 4 re-seats `params` directly and reads none of it), but any future test touching load/save inherits test 3's "user edits" — exactly the class-4 trap.
Fix: Reset `paramEdits: {}` (and the vram fields) in the same `beforeEach`.
CONFIRMED (state flow traced; current inertness noted).

Refuted during verification pass (deleted): fixture rot against the c001de9 queueStore rewrite (the `Job` fixture still matches the current interface — `startedAt`/`preflight`/`cfgOverride` are optional, `workflow: {}` is assignable to `Record<string, …>`; file runs green); React `change`-event vacuousness in test 3 (the 89/input/chip triple can only pass if onChange→commit→setParam→snap→re-render all ran — proven by the live run); `button[title*='Queue']` colliding with the "1 at a time" title (lowercase "queue." does not case-match); tautologies in test 1 (`?.disabled).toBe(false)` fails as `undefined` if the selector misses).

## Missing safeguards
- The Queue render click path is never fired: no test clicks the enabled button and asserts `queue()` was invoked, a job appears, and the button flips to disabled "Render in progress". Store logic is covered in `src/stores/stores.test.ts`, but the surface wiring (`DeckControls` onClick → `queueRender` → store) is unguarded anywhere — dropping the onClick binding leaves all 4 tests green.
- The `lastQueueError` danger chip (GenerateSurface.tsx line 202) is untested — a failed queue attempt's user-visible surfacing on Generate has no assertion (the store setting it is covered, its rendering is not).
- Prompt/negative textarea bindings (`setPrompt`/`setNegative`, GenerateSurface lines 74-93) — the screen's primary input — are never typed into.
- The Randomize seed switch (`toggleRandomize`, aria-checked label flip) is untested.
- The snap chip's 4-second auto-dismiss (GenerateSurface lines 38-43) is unguarded: test 3 asserts only appearance, so a regression that never clears the chip (or clears it immediately) passes.
- No `afterEach` removes the four appended `host` divs from `document.body` (inert today — queries are host-scoped — but pure hygiene debt).
- A `queued` (not `running`) job's "queued · waiting" status line and the `untrackedBusy` ("server busy · N untracked") line are never exercised on this surface.

context-pack: read current bytes of GenerateSurface.test.tsx, GenerateSurface.tsx, DeckControls.tsx, queueStore.ts, bundlesStore.ts, Stepper.tsx, constraints.ts, AdvancedDrawer.tsx, enums.ts, ScreenStage.tsx, vitest.setup.ts, api/types.ts (ApiWorkflow); git log for the test file (last touched 110acee 2026-08-19, one month before queueStore rewrite c001de9 2026-09-17); sibling coverage grep (stores.test.ts, OutputsSurface.test.tsx, QueueSurface.test.tsx, DeckControls.test.tsx); live run `npx vitest run src/surfaces/GenerateSurface.test.tsx` → 4 passed.
new-findings: 3
