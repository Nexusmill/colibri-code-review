<!-- source: src/bundles/schema.ts | reviewer: glm-5.3-zai-in-session | sha256: 33e6a4f4828252c5be63c835652a5136123fc14620eae49ca6bb8d6fa2ab6f12 | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

All traces complete. The migration's only untested interplay is custom detents x adopted `frames_max` — and the math confirms the collision (521 on "4n+3" snaps to 523). Everything else in the hunt list was refuted end to end.

## Verdict

The validator itself is tight (ids, detents, the new vocabulary, presets, round-trip all hold up at every call site), but the new `withFactoryConstraints` migration adopts the factory `frames_max` without consulting the bundle's own detent, so for custom-detent files it produces a list its own validator rejects — and the store's containment converts that into a permanent, silent loss of the entire vocabulary migration. Shippable after fixing that one defect.

## Fixed since last review

- Prior review (d0cc311e @ e3a2c03, 2026-09-05) reported no findings ("None (delta is a comment...)") and the review before it left no open findings — nothing to close. Its "prior review's notes stand" bullet also carried no open items. Verified against the current file: the gate-proof comment is still the last line (schema.ts:338).

## Bugs & vulnerabilities

**[MEDIUM] withFactoryConstraints adopts factory frames_max blindly onto a custom detent — the whole migration is then silently discarded on every load** - `line 113`
- What: The frames_max adoption (schema.ts:113-116) checks only `frames_max === undefined` and `defaults.frames <= 521`; it never consults the bundle's own `constraints.frames` detent. The new validator (schema.ts:189-191) rejects any `frames_max` that doesn't sit ON the detent. The factory cap 521 is on `8n+1` but not on custom detents — `snapToDetent(521, {k:4,c:3})` = 523 != 521.
- Trigger: bundles.json hand-edited so the `LTX-2.3-Distilled` bundle keeps a custom detent (e.g. `"4n+3"` — exactly the custom-detent class constraints.ts:54-59 designs its fallback for) and `defaults.frames <= 521`. Load: `validateBundles` passes the raw file (no frames_max yet), `withFactoryConstraints` merges 521 in, the recheck at bundlesStore.ts:127 fails the off-detent cap, and bundlesStore.ts:128-131 drops the merge — for every bundle, silently, and repeats identically on every load (nothing is persisted, nothing is spoken).
- Impact: The doc's own invariant is false ("the migration can never invalidate an existing config", schema.ts:90-93 — it can; only the store's recheck contains it), and the collateral is real: no bundle in that file ever adopts any vocabulary bound — the Qwen 8-grids, steps bounds, size presets, and lora_strength all stay absent, so off-grid widths keep rendering cropped/padded, the exact harm this feature exists to prevent. No corruption persists; the harm is permanent silent degradation. schema.test.ts covers off-detent refusal (line 100) and both adoption paths (lines 139-187) but never a custom detent through the migration.
- Fix: In the frames_max branch, either skip adoption when the file declares a detent the cap doesn't sit on, or floor the cap onto the file's detent exactly as the runtime fallback already does (constraints.ts:57-59: `Math.floor((521 - c) / k) * k + c`). CONFIRMED (adoption condition, snap math 521->523 on 4n+3, and the store discard path all traced end to end).

## Missing safeguards

- `defaults` positivity is never validated: the new on-grid checks (schema.ts:196-197) pass `width: 0` and on-grid negatives (`-16 % 16 === 0`), and `steps`/`cfg` only get `typeof` checks (schema.ts:164). A corrupt import validates "ok" and is repaired only later by boot-time `coerceParams` (bundlesStore.ts:141) and render-time `violations()` — bundles.json itself can hold values the schema's own constraint philosophy calls illegal.
- `defaults.frames` is never checked against the bundle's own detent (only against `frames_max`, schema.ts:200); an off-detent default rides through load and is snapped silently at boot rather than refused like every other defaults-vs-constraint violation.
- The preset-label dedup (schema.ts:214-215) maps missing labels to `""`, so two malformed presets add a spurious "labels must be unique" issue on top of their per-preset refusals (cosmetic; the file is already rejected).
- No test exercises a custom detent through `withFactoryConstraints` — the one case where adoption and validation disagree (the MEDIUM above).
- `fps` is only `typeof`-checked (schema.ts:167): `fps: 0` or negative passes validation for video+audio bundles (pre-existing hole the new defaults-satisfy-constraints family did not close; render-time `violations()` catches it).

context-pack: delta = e7bc621 only (constraint vocabulary, withFactoryConstraints, preset/lora_strength validation, snapToDetent import); consumers verified — bundlesStore load/save re-validate (incl. post-migration recheck that contains the finding), vite.caliper.ts:88 PUT validates server-side, BundlesSurface.tsx:126-158 import walks validateBundles singleton + collision-blank + editor gate, AdvancedDrawer spreads the full bundle (lossless round-trip), fill.ts:113 consumes `lora_strength ?? 1`, constraints.ts parseDetent regex-coerces non-strings safely and framesMax() floors its fallback onto the detent; no parseInt/Number coercion hazards found.
new-findings: 1
