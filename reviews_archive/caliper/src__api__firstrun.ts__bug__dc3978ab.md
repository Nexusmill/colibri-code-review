# Colibri bug review — src/api/firstrun.ts

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: dc3978abb0eb409f43aeed1f55f9e11526927bb17af8cc6c18d08a75410a61ff

### Meta
- path: src/api/firstrun.ts | sha8: dc3978ab | lines: 14 | context-pack: 3 importers (App.tsx:35 boot-time GET with silent catch; FirstRun.tsx + FirstRun.test.tsx via `completeFirstRun`); server route `handleFirstRun` at vite.caliper.ts:426-447 (GET `{done}` by file presence, POST writes the file, 405/500 otherwise), mounted in BOTH `configureServer` and `configurePreviewServer` (vite.caliper.ts:634-641) so the preview-served desktop build reaches it; git: single-commit file (91620a1).

### Review

## Verdict
**PASS.** The client mirrors the server contract exactly (endpoint, method, `{done}` shape, throw-on-`!ok`), and every consumer handles the throwing contract deliberately: the wizard's own exit paths await and surface failure ("the done record did not save", FirstRun.tsx:118-126), fire-and-forget paths self-heal via next-boot reoffer, and the record is presence-semantics server-side so the concurrent double-POST (button + deferred unmount recorder) cannot corrupt meaning. No race, no missing await, no wrong endpoint.

## Bugs & vulnerabilities

- **[LOW] Failed first-run check silently skips the offer for that boot, with no trace and no retry** - `line 6-8` — CONFIRMED
  - **What:** `getFirstRun` rejects on any non-OK response; App.tsx:41 catches with an empty handler ("the record could not be read - never block boot").
  - **Trigger:** Preview/dev server briefly unavailable at app boot, or a 500 from the middleware's `catch` (e.g., transient EBUSY reading `caliper.firstrun.json`).
  - **Impact:** The one-time wizard does not appear that boot. It is NOT "skip forever" — nothing is recorded on the error path (no POST fires), so the next boot re-checks, and SETTINGS · FIRST RUN re-runs it any time (server comment, vite.caliper.ts:421-423). The concrete harm is limited to: zero observability (no `console.error`), and a user who closes the app after a single errored boot never sees the offer unprompted.
  - **Fix:** Add a `console.warn` (or surface to the status line) in the App.tsx catch; optionally retry once after a short delay. No change to firstrun.ts itself is required — the throwing contract is correct.

## Missing safeguards
- `getFirstRun` line 8 does an unvalidated `as { done: boolean }` cast. If the endpoint ever 200s with a body lacking `done`, `undefined` coerces falsy → wizard opens (bounded self-correction: any exit records done server-side). Cheap hardening: `typeof j.done === "boolean"` guard in the client or a `done: true` literal check.
- Neither fetch has a timeout/`AbortSignal`. A hung localhost connection means the wizard silently never opens (`void`ed promise) or an exit recorder never fires. Low practical risk on localhost.
- Appsec note, scoped honestly: the POST write (vite.caliper.ts:435) checks no `Origin`/`Host`, so a malicious page could cross-origin form-POST `http://localhost:4173/api/firstrun` (form posts need no CORS) and suppress the wizard. Impact is negligible (skippable wizard, no data), consistent with the app's localhost threat model — listed only for completeness alongside every other unauthenticated middleware write.
