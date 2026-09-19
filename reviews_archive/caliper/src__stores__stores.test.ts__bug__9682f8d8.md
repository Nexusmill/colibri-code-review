<!-- source: src/stores/stores.test.ts | reviewer: glm-5.3-zai-in-session | sha256: 9682f8d825f13d5906eee2127af9abd4645d66254d6c6fd80a8f2ec2bc143e9e | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: TESTFILEHUNT - the first colibri bug hunt on TEST files (top 10 by guarded-module fan-out); fresh-context pass, no prior bug review existed. -->

## Verdict (1-2 sentences)
This file is substantially sound — the BUGHUNT12-era tests (clobber pin, disconnect reconcile, promotion, closeByPrefix) genuinely pin the new record-verb and reconcile behavior, and a live run passes 32/32. The real defects are protection-weakening, not protection-faking: one fixture bug makes a named protection exercise the wrong code branch, and the file's cross-test hygiene (store resets, stub teardown, stub-before-act) leaks state that is only accidentally masked today.

## Bugs & vulnerabilities

**[MEDIUM] Duplicate-id fixture makes the "reselects the first remaining" test exercise the id-carry branch instead** - `line 247` (fixture 244-251, assertion 252)
- What: `const b = { ...a, name: "B" }` copies `a`'s `id: "A"`, so the seeded `bundles: [a, b]` contain duplicate ids — a state `validateBundles` would reject ("Duplicate bundle id", schema.ts:255) and production can never produce. Traced through `save()` (bundlesStore.ts:212-221): `prevSel` = b (id "A"), `carried = list.find(x => x.id === "A")` finds `a`, so `selected` becomes "A" via the **carry branch**, not the promised fallback branch (`list.some(name === selected) ? … : list[0]?.name`).
- Trigger: run the test with the fixture as-is; trace `carried` — it is truthy, so the `list[0]?.name ?? ""` fallback named in the title never runs.
- Impact: if the "reselect first remaining" fallback regressed, this test still passes — both branches happen to yield "A". The fallback branch is exercised by no other test in the file (test at line 226 keeps an in-list selection; test at line 283 tests the carry path deliberately). The test's name promises protection it does not provide.
- Fix: give `b` its own `id: "B"` so `carried` is undefined and the fallback is what's pinned (both assertions and outcome stay identical, but the right branch is under test).

**[MEDIUM] beforeEach resets only bundlesStore — queueStore/screenStore/uiStore state leaks across every test** - `line 9` (lines 9-16)
- What: `beforeEach` clears localStorage, provenance, and bundlesStore, but never `useQueueStore` (`jobs`, `socketState`, `lastQueueError`, `singleGuard`), `useScreenStore`, or `useUiStore`; module singletons (`queueInFlight`, `rejectSeq`, `selectGen`) also persist. Traced leaks: the queue-rejection test (line 100) prepends a `rejected-*` failed job that survives into later tests; the reconcile test (line 369) leaves 4 terminal jobs plus `socketState: "connected"`; the guard-off test must manually restore `singleGuard: true` at line 365 precisely because nothing else does; the reconcile test must hand-set `socketState: "disconnected"` at line 402 or `setSocketState("connected")` would be a no-op (`was === "connected"`) and the whole test would fail for an ordering reason.
- Trigger: any assertion failure before a test's manual cleanup (e.g., line 365, 464), or any future test that reads `jobs`/`socketState`/`singleGuard` without seeding them.
- Impact: test-order dependence — results depend on execution order and on every earlier test passing its clean-up tail; a failed test mutates the environment of the next. A stale `"connected"` socketState would silently disable a future reconnect-reconcile test's act.
- Fix: extend beforeEach to `useQueueStore.setState({ jobs: [], socketState: "connecting", lastQueueError: null, singleGuard: true })` (and equivalents for screen/ui stores, plus bundlesStore's `vramNote`/`vramPrompt` which the VRAM tests each hand-reset).

**[LOW] `vi.unstubAllGlobals()` sits only on the success path and the config has no `unstubGlobals: true`** - `line 107` (pattern at 32, 107, 136, 168, 212, 240, 253, 269, 291, 312, 348, 366, 417, 494, 514, 534, 549, 565; vite.config.ts:38-42)
- What: every fetch-stubbing test unstubs after its final assertion. vite.config.ts's `test` block sets only `environment`/`globals`/`setupFiles` — vitest's `unstubGlobals` defaults to false, so an assertion thrown at, say, line 102 or line 411 leaves that test's `fetch` stub installed for all subsequent tests.
- Trigger: make any stubbed test fail mid-body; the next test's unstubbed fetch calls (e.g., the provenance POSTs in the un-stubbed tests at lines 140, 217) hit the previous test's stub.
- Impact: currently masked (later tests stub their own fetch or make none before stubbing), but a failure cascade reports the wrong first cause, and a leaked stub can make a later test's incidental network calls "succeed" vacuously.
- Fix: add `unstubGlobals: true` to the `test` block in vite.config.ts (or an `afterEach(() => vi.unstubAllGlobals())`).

**[LOW] Real (unstubbed) fetch is invoked before the stub exists in the reconcile test** - `line 374` (374-376)
- What: `saveProvenance` at lines 374-375 fires `void send("POST", …)`, and `send` (provenance.ts:49-57) evaluates `fetch(...)` synchronously before its first `await` — i.e., against the real global fetch, since `vi.stubGlobal` happens only at line 376. The test works by accident: Node's undici rejects the relative URL `/api/provenance` and `send`'s catch swallows it.
- Trigger: trace any `saveProvenance` call made before the stub line; the POST never reaches the stub.
- Impact: no assertion lies (the assertions read the synchronous cache, not the POST), but the test's environment behavior is an accident of undici's relative-URL rejection — a fetch polyfill with a base URL would turn these into live network calls from a unit test.
- Fix: install the fetch stub before the first `saveProvenance` (the tests at lines 140 and 217 also fire real fetches, but there no stub is intended at all — acceptable if deliberate).

**[LOW] nodeType assertion pins the empty-workflow fallback echo, never the class_type resolution it appears to test** - `line 80` (fixture `workflow: {}` at line 75)
- What: `expect(job.nodeType).toBe("7")` runs against a job whose `workflow` is `{}`, so production (`String(job.workflow[e.nodeId]?.class_type ?? e.nodeId)`, queueStore.ts:203) answers via the `?? e.nodeId` arm — the assertion verifies nodeId echoed as nodeType, not lookup. The one fixture that does carry a `class_type` ("VAEDecode", line 425) never asserts `nodeType`.
- Trigger: break the `job.workflow[e.nodeId]?.class_type` lookup entirely (always fall through to `e.nodeId`); this test still passes.
- Impact: the class_type-resolution branch of the executing handler is untested file-wide while the file reads as though it is covered.
- Fix: give the line-75 fixture `workflow: { "7": { class_type: "VAEDecode", inputs: {} } }` and assert `nodeType` is `"VAEDecode"` (or assert nodeType in the line-421 test).

## Missing safeguards
- The `setTimeout(10/20)` sync points (lines 405, 490, 510, 528) are currently deterministic, not races — every stubbed chain is microtask-only, so the macrotask timer fires after the whole chain drains (verified: the full 32-test file runs in 122ms). But the guarantee is implicit: one future stub or store debounce containing a timer turns these into flaky races with no signal at the sleep. Awaiting a store predicate (poll `getState`) or exposing the reconcile promise would make the sync structural.
- `clearAll` test (line 346) asserts `POST /queue` occurred but not the body `{ clear: true }` (client.ts:143-150) — `cancelQueued` also POSTs /queue, so the test cannot distinguish "emptied the server queue" from "cancelled one id".
- The "survives reloads" test (lines 226-241) verifies only the persist WRITE half; the rehydrate/READ half (`onRehydrateStorage` merging `paramEdits` into `params`, bundlesStore.ts:342-354) is exercised by no test in the file — no second store instance is ever created from the persisted key.
- `doHydrate`'s server-side non-array guard (provenance.ts:64, added in the same BUGHUNT12 commit) is untested — the corrupt-seed test (lines 172-180) covers only the `legacyRecords` localStorage path.
- Stale comment at line 119 says provenance "PUTs" hit fetch; the store now POSTs/PATCHes/DELETEs — harmless today only because the stub's fallback `Response("[]")` swallows every verb.
- Queue tests feed `/api/preflight` responses that are structurally wrong for `VramPreflight` (e.g., line 356's stub returns `{prompt_id}` for every URL); the parsed-but-garbage preflight is stored on the job and never asserted — a broken preflight parse would pass silently.

context-pack: stores.test.ts (current on-disk bytes, all 624 lines), provenance.ts, queueStore.ts, bundlesStore.ts, screenStore.ts, uiStore.ts, api/client.ts (getHistory/getLiveQueueIds/queuePrompt/clearQueue/cudaFreeGb/freeVram/getVramPreflight), api/types.ts (WsEvent), bundles/schema.ts (validateBundles empty-array message, duplicate-id check, defaultBundles factory values for the migration fixture), bundles/constraints.ts (snapToDetent/snapMessage/coerceParams), bundles/files.ts (validateFiles robustness against garbage ObjectInfo), vite.config.ts test block, vitest.setup.ts (localStorage shim), git log for the file (c001de9 extension confirmed), live `npx vitest run` (32/32 passed, 122ms — fixture-rot check).
new-findings: 5
