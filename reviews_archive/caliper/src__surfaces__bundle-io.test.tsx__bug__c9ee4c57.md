<!-- source: src/surfaces/bundle-io.test.tsx | reviewer: glm-5.3-zai-in-session | sha256: c9ee4c5757d3c4c280b907943e6a6c088d83eafe6e75d3cd4ce0e71a0defc687 | date: 2026-09-17 | mode: bug -->
<!-- context: owner commission 2026-09-17: TESTFILEHUNT - the first colibri bug hunt on TEST files (top 10 by guarded-module fan-out); fresh-context pass, no prior bug review existed. -->

## Verdict
The file is fundamentally honest — all four tests drive real production paths (real blob payload parsed, real store transitions, real editor DOM) and pass live — but its protection is materially thinner than its titles claim: the id half of the collision contract is completely dark, the export envelope is never proven re-importable, and test 1 permanently mutates the global `URL` object under the guise of a restorable stub.

## Bugs & vulnerabilities

**[MEDIUM] Title promises "keeps its own id" — no assertion ever touches an id** - `line 92`
- What: Test 3's contract is "takes a visible name suffix AND keeps its own id"; the only assertion (line 98) checks `nameInput.value`. The id is asserted nowhere in the file, and the editor (AdvancedDrawer.tsx:27) renders only `name`, so the id is invisible to every query used.
- Trigger: Any regression in BundlesSurface.tsx:155 (`if (bundles.some((x) => x.id === incoming.id)) incoming.id = ""`) — e.g. blanking the id on EVERY import, or inverting the condition so colliding ids are kept — plus any id-mangling in the import chain.
- Impact: Both imports use the non-colliding id `"tuned-away"` (no default bundle has it, per schema.ts:268-366), so the collision-blanking path never executes and an id-destroying regression keeps the whole file green. Since ids are the immutable template key (schema.ts:41-43), silent id loss breaks provenance/template lookups with zero test alarm.
- Fix: In test 3 (or a new test), click "Save bundle" with the fetch stub and assert `useBundlesStore.getState().bundles.find((b) => b.name === "LTX-2.3-Distilled (loaded)")!.id` equals `"tuned-away"`; add a companion case importing a bundle whose id collides with a factory id, asserting the id comes back non-colliding after save.

**[MEDIUM] Global `URL` mutation outlives test 1 — the "stub" is never undone** - `lines 54-59, 71-72`
- What: `vi.stubGlobal("URL", Object.assign(URL, { createObjectURL, revokeObjectURL }))` mutates the real global URL constructor's statics in place and then stubs the global with that same object. `vi.unstubAllGlobals()` (line 71) restores the globalThis.URL *reference*, which IS the mutated object — the two stub closures (capturing test 1's `created`/`revoked` arrays) remain installed for the rest of the file. `origURL` is captured (line 54) and voided (line 72) but never re-assigned: dead code marking an intent that never executes.
- Trigger: Any test running after test 1 in this file that triggers a download (clicking "save as file").
- Impact: None today (tests 2-4 never press "save as file" — verified), but this is exactly the cross-test contamination trap the file must not ship: a future download test would silently satisfy `createObjectURL` against test 1's leftovers or push into test 1's arrays post-hoc, manufacturing a vacuous pass.
- Fix: Save both originals and restore them in a `finally`/`afterEach` (`URL.createObjectURL = origCreate; delete URL.revokeObjectURL` as appropriate), or stop mutating: build the stub on a fresh object spread and restore via `vi.unstubAllGlobals()` only if the whole object was replaced.

**[LOW] Fixed 25ms sleeps race the async acts** - `lines 36, 42, 64, 86`
- What: `tick()` (25ms) is the only synchronization for jsdom's FileReader round trip + `loadFile`'s await chain (line 42) and for the save pipeline `fetch → getObjectInfo → validateFiles → set` (line 86).
- Trigger: FileReader/fetch resolution slower than 25ms on a loaded CI machine.
- Impact: Spurious failures (flake), not vacuous passes — assertions are real. PLAUSIBLE breach (mechanism confirmed by code; the timeout exceedance is environment-dependent — the file passes in 309ms locally).
- Fix: Poll for the assertion target inside `act` (await a condition loop, waitFor-style) instead of a fixed sleep.

**[LOW] Cleanup only runs on the success path** - `lines 70-73, 88-89`
- What: `clickSpy.mockRestore()`, `vi.unstubAllGlobals()`, and unmount are sequential statements after the assertions, with no `try/finally` or `afterEach` net.
- Trigger: Any assertion failure in test 1 or test 2.
- Impact: The anchor-click no-op spy and — worse — test 2's catch-all fetch stub (`Response("{}", {status:200})` for every URL) leak into subsequent tests, turning the next failure diagnosis into a lie about which network the later tests saw.
- Fix: `afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); })`.

**[LOW] Envelope assertions weaker than "self-describing"** - `lines 67-69`
- What: The title promises a self-describing envelope; the checks are `bundle.name` equality and `defaults` `toBeDefined()`.
- Trigger: A regression that omits a field `validateBundles` requires on import (text_encoders, vae, loader, constraints grid agreement — schema.ts:181-250).
- Impact: Export's test stays green while the exported file is refused at LOAD FROM FILE — the round-trip, which is the feature's entire reason to exist (commit c044ce3), is unguarded. CONFIRMED as an assertion-strength gap.
- Fix: `expect(validateBundles({ bundles: [parsed.bundle] }).ok).toBe(true)` — one line, imports already available.

**[LOW] The PUT is never asserted to have hit the wire** - `lines 84-87`
- What: The fetch mock is installed but never inspected (no `toHaveBeenCalledWith` checking `method: "PUT"`/body); the post-save assertion only reads store state, which `save()` sets after `res.ok`.
- Trigger: A regression where the store sets `bundles` without persisting (dropping/short-circuiting the PUT in bundlesStore.ts:192-196).
- Impact: The write-the-user-believes-in (the server-owned bundles.json) can silently stop persisting while the gate test stays green. CONFIRMED as weaker-than-title ("nothing writes until Save" is verified store-side at line 83 — that half is honest — but the actual write is only implied).
- Fix: Capture the mock (`const fetchMock = vi.fn(...)`), assert one PUT to `/api/bundles` with the expected body after the save click.

## Missing safeguards
- No coverage of the id-collision blanking branch (BundlesSurface.tsx:155) — both fixtures import a non-colliding id, so the feature's one conditional id path is dark.
- No export→import round-trip: the produced envelope is parsed but never fed back through `loadFile`/`validateBundles`.
- Anchor `download` filename contract (`${b.id || b.name}.caliper-bundle.json`, BundlesSurface.tsx:130) unasserted — the "move between machines" affordance includes the extension-based file recognition.
- `toHaveLength(4)` (line 83) hardcodes the factory catalog size; adding a fifth factory bundle breaks this test for an unrelated reason — compare against a pre-act snapshot of the store instead.
- No test that a *refused* save (server returns issues) keeps the editor open and speaks the issues — the import flow's failure exit is only covered for file-parse errors (test 4), not save-time validation refusals.
- The second-collision dedup suffix (`(loaded) 2`) is untested — minor depth gap behind the tested first suffix.
- No `afterEach` global/mock restoration net (see finding 4); `beforeEach` also never resets `paramEdits`, currently harmless only because no test writes it.

context-pack: bundle-io.test.tsx (sha c9ee4c57, current bytes, one commit c044ce3), BundlesSurface.tsx (saveFile/loadFile/collision lines 125-168), bundlesStore.ts (save/load gates), bundles/schema.ts (validateBundles + defaultBundles 4-bundle fixture), bundles/enums.ts + install/client.ts + api/client.ts (mount-time fetch paths), bundles/files.ts (validateFiles with empty ObjectInfo), components/AdvancedDrawer.tsx (name input), vitest.setup.ts (localStorage/scrollIntoView shims), .colibri_reviews/_manifest.json (no prior entry for this file), live vitest run of the file (4/4 passed, 309ms).
new-findings: 6
