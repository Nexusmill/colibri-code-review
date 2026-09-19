<!-- source: src/surfaces/OutputsSurface.test.tsx | reviewer: glm-5.3-zai-in-session | sha256: 3b7a074afb6bbd356930b98ff03d70c497b33a8ecb7d3fbc0bdb6ec11c089f10 | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: TESTFILEHUNT - the first colibri bug hunt on TEST files (top 10 by guarded-module fan-out); fresh-context pass, no prior bug review existed. -->

## Verdict
Mostly yes: tests 3 and 4 trace real production paths end-to-end (OPEN carries to the render screen; a real `queue()` call stamps OVERRIDE), but three of five test names promise protection the assertions never deliver. Single biggest risk: the archive's core structure — kind·day grouping and kind classification (`kindOf`/`modelGroups`) — is completely unasserted while test 2's name claims it, so the surface's signature organization can regress silently.

## Bugs & vulnerabilities

**[MEDIUM] Test name promises "kind·day group"; no grouping assertion exists — `line 29` (assertions `lines 49-59`)**
What: The test asserts only `video`/`audio` elements, `seed 42`, absence of "Copy settings", and the REPRODUCE click. Nothing checks the group header (`VIDEO · <date>`, rendered via `.lib-group` at OutputsSurface.tsx lines 193-204, 243-248).
Trigger: Any regression in `kindOf` (video/image/audio priority), `pickFiles`, the day bucketing (`toLocaleDateString` map), or `modelGroups` ordering — e.g., a card landing under "SOUND ·" or groups flattened entirely.
Impact: The test passes while the archive's defining structure is wrong; the video-vs-audio classification that decides a render's home is unpinned anywhere in this file.
Fix: Assert `host.textContent` contains the exact group label `VIDEO · <today's date>` and that no `SOUND ·`/`IMAGES ·` group exists for this fixture. CONFIRMED (traced: no "VIDEO" string anywhere in the test file).

**[MEDIUM] "fetched once per record across job updates" — the job updates cannot trigger a fetch; the per-record guard is unprotected — `lines 151-154`**
What: `hydrate()` is called only in the mount effect (OutputsSurface.tsx line 152, deps `[]`); the two `useQueueStore.setState` acts (lines 151-152) cause re-renders only, zero fetches. The count of 1 is produced entirely by the StrictMode double-mount sharing one in-flight hydrate (assetsStore.ts lines 32, 39).
Trigger: Delete the `hydrated` set (assetsStore.ts lines 23, 44, 53 — the actual "once per RECORD" dedup) and re-run: still 1 call, still green, because nothing ever re-invokes hydrate after mount.
Impact: The name's central guarantee ("once per record across updates") is vacuous; only the concurrent-mount in-flight sharing is genuinely tested. Yesterday's c001de9 rewrite of the hydrate/refresh path left this test passing for a reason other than the one it states.
Fix: Drive a second hydrate explicitly (call `useAssetsStore.getState().hydrate()` again after the job updates) and keep the count at 1 — that pins the `hydrated`-set dedup the name advertises. CONFIRMED (traced end-to-end through OutputsSurface.tsx and assetsStore.ts).

**[LOW] "empty state directs to Generate" — the asserted empty state contains no direction, just copy — `lines 14-25`**
What: The one-off empty state is a plain `<p>` (OutputsSurface.tsx line 241) with no link, button, or navigation; the test pins only `toContain("No one-off renders yet.")`.
Trigger: The name is a fossil of an older affordance; today "directs" is a verbal mention inside paragraph copy.
Impact: The test blesses a directionless empty state, contradicting both its own name and the repo's stated empty-state rule ("invitations with their own next click"). If a click-to-Generate affordance is ever added and then lost, nothing fails.
Fix: Either rename to "empty state names where renders come from" or assert a real affordance (button/link navigating to Generate) once one exists. CONFIRMED.

**[LOW] Cross-test state leakage on failure paths — cleanup only after assertions, no afterEach — `lines 60, 92-95, 99-101, 121, 155`**
What: `closeReproduce()` (60), the windows/jobs/provenance reset (92-95), and both `vi.unstubAllGlobals()` calls (121, 155) run after assertions; test 4 never resets `jobs` at entry (99-101), relying on test 3's tail cleanup. vitest config (vite.config.ts test block) has no `unstubGlobals`/`restoreMocks`, and there is no `afterEach` in the file.
Trigger: Any assertion failure in tests 2-5 skips cleanup: `reproduce` stays set and `ReproduceSheet` renders inside every later mount; `fetch` stays stubbed; done jobs leak forward.
Impact: Today the leaks are absorbed (later tests re-clear provenance/localStorage, re-stub fetch; the leaked sheet for item p1 renders no `text-danger` span, so test 4's `span.text-danger` query survives), but one small component change (e.g., a `text-danger` span in ReproduceSheet) converts any single failure into cascading false failures across the file.
Fix: Move all resets into a single `afterEach`: `useScreenStore.setState({ windows: [], reproduce: null })`, `useQueueStore.setState({ jobs: [] })`, `resetProvenance()`, `resetHydrated()`, `localStorage.clear()`, `vi.unstubAllGlobals()`. CONFIRMED.

## Missing safeguards
- No afterEach resetting the module singletons (screenStore `windows`/`reproduce`/`openedJobs`, uiStore `surface`, assetsStore `items`, `hydrated`); every cleanup is inline and success-path-only.
- FILM ASSETS division entirely untested: no test seeds a film (filmList stub), so `FilmPanel` type ordering (TYPE_ORDER), `reproduceFilm`'s autopilotStatus flow, and the ownership filter `!it.outputs.some(o => o.type === "film")` (OutputsSurface.tsx line 176) — a deliberate bug-fix guard — are unpinned.
- The lens/filter (`lens`, `filmHits`/`oneOffHits`, the match-count placeholder) and SHOW IN LIBRARY cross-link have zero coverage.
- Test 4's universal fetch stub returns `{prompt_id: "ov-1"}` to every route, including `/api/preflight` (parsed as a `VramPreflight` with undefined verdict/say) — harmless today, fixture-rot-prone; and the test never inspects the fetch mock's methods/URLs, so yesterday's record-verb rewrite (POST/PATCH in provenance.ts `send()`) is unverified here.
- Test 4 fixture couples to `defaultBundles.bundles[1]` positionally (should select by id/name); it fails loudly today only because a video+audio bundle at that index would throw on missing frames.

context-pack: OutputsSurface.test.tsx (full read); OutputsSurface.tsx; stores provenance.ts, queueStore.ts, screenStore.ts, uiStore.ts, assetsStore.ts; api/client.ts (getHistory, queuePrompt, getVramPreflight, viewUrl); api/film.ts (filmList); bundles/schema.ts, bundles/constraints.ts, workflows/fill.ts (cfgOverride trace); components MediaView.tsx, ReproduceSheet.tsx; vitest.setup.ts, vite.config.ts test block; git log for test file, OutputsSurface.tsx, and c001de9 --stat.
new-findings: 4
