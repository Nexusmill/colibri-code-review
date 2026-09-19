<!-- source: src/api/modelRoutes.ts | reviewer: glm-5.3-zai-in-session | sha256: 35f2e54fd3d8b7ee8db17daa8814a3fc9dbaa9bf5056781834e75de7ee2f1add | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the NEXT top ten files by import PageRank (the board past the hunted ten); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; same-sha files hunt beyond the record). -->

## Verdict
Clean — no new defects. Every draft died in Phase 3 refutation; the file is a thin, consistently-guarded fetch client whose five cross-file contracts (GET shapes, price object, profile enum, health keys, preset returns) all verify against the live middleware and consumers.

## Bugs & vulnerabilities
- None new beyond the record. Phase-3 refutations, so the next hunter does not re-chase them:
  - "getModelSchema ok-path has no payload guard → ModelPicker RUN armed on a hollow form → billed empty-input run" — REFUTED: the RUN button renders only inside `{schema && (…)}` (src/components/ModelPicker.tsx:315-336), so a null/failed schema can never produce an armed RUN; and a 200-with-unparseable-body is unreachable through vite.replicate.ts's `send()` (always `JSON.stringify`; handler throws land in the JSON 500 catch).
  - "runCloudModel leaves `bytes` unvalidated → 'NaN KB' truthful-status text" — REFUTED: vite.replicate.ts:261 sends `bytes: data.length` atomically with `file` in the same response object; the `!data.file` check at src/api/modelRoutes.ts:92 gates the pair.
  - "routePreset returns unvalidated ok body" — REFUTED: all three SettingsConsole consumers guard (`r.presets ?? []` at lines 250/263, preset-apply re-fetches through getRoutes at line 236-237); the server's 200s never omit these fields.
  - "health key mismatch between writer and reader" — REFUTED: writers emit `replicate/${slug}` / `openrouter/${slug}` (vite.film.ts:810, 922, 968), readers build exactly `${r.service}/${r.cloudModel}` (SettingsConsole.tsx:135, 277).
  - "FirstRun could pass a third profile value" — REFUTED: `TierVerdict.profile` is exactly `"cloud-only" | "multimodal"` (src/install/tiers.ts:28), the enum the server accepts.
  - `post()` last-write-wins on model-routes.json is recorded as known/unchanged in the vite.routes.ts review — not restated.

## Missing safeguards
- `getModelSchema` (line 85) is the only fetcher in the file without an ok-payload check — its siblings verify `!data.config` / `!data.file`, it verifies only `res.ok`. A future server change to 200-with-`{error}` or an empty body would resolve "success" with a hollow `ModelSchema`; one guard (`!res.ok || !data.slug`) would make the family uniform.
- `runCloudModel` (lines 92-93) validates `file` but not `bytes`, and both consumers immediately compute `(r.bytes / 1024).toFixed(0)` status text (ModelPicker.tsx:285-286, CloudPane.tsx:90-91) — a dropped `bytes` would print "done - NaN KB joined the library", against the truthful-status rule. Currently unreachable (see refutation); a `?? 0` would pin it.
- No fetch is cancellable (no AbortSignal anywhere): a stray or regretted paid RUN cannot be withdrawn client-side once POSTed; acceptable for long cloud runs, but the money path has no client-side undo.
- `TypeInfoUi.resolved` (line 24) is populated by the server on every GET and read by no consumer in src — dead payload weight on the wire; either wire it to the deck rail (its stated purpose) or drop it from the interface.

context-pack: jcodemunch local/Caliper importers (11 files) + vite.routes.ts/vite.replicate.ts/vite.keys.ts handlers + routesStore/ModelPicker/CloudPane/SettingsConsole/FirstRun/tiers.ts consumers read at cited lines; git head cbd6eaf; prior same-sha review loaded (clean verdict).
new-findings: 0
