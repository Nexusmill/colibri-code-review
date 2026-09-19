<!-- source: src/bundles/constraints.ts | reviewer: glm-5.3-zai-in-session | sha256: e75972de463a5f14e763f615c37752962c2874004f586acfd597d79c6ae831e5 | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the top ten files by import PageRank (the 2026-09-14 board); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; delta files report new/changed only + close the loop; same-sha files hunt beyond the record). -->

All traces are closed. Budget spent on the three consumer paths (fill.ts build-time throw, bundlesStore boot coercion + setParam cap speech, GenerateSurface ceiling) and the schema twin — the schema validates most of the vocabulary edges I drafted, refuting them. One arithmetic edge survives refutation.

## Verdict
Shippable — the new constraint-vocabulary accessors are twin-consistent with schema.ts's validation (positive-integer multiples, on-detent ceilings, ordered step bounds), and the one surviving defect is a hand-edit edge that bricks only its own bundle with a truthful refusal. No render-path or coercion defect reaches a user with factory or ordinary hand-edited files.

## Fixed since last review
- Prior review (01434323) carried **no open findings** — nothing to close. Its blessed behavior (violations/snapMessage quoting `b.constraints.frames`) is intact at current lines 103 and 126, verified-stale as an action item.

## Bugs & vulnerabilities
**[LOW] framesMax fallback can go negative for a schema-legal pathological detent, and coerceParams then seats a negative frame count** - `line 59`
- What: the undeclared-`frames_max` fallback `Math.floor((521 - det.c) / det.k) * det.k + det.c` is unbounded below as `c` grows; it is only guaranteed <= 521, never >= 1. For a hand-edited detent like `"1000n+900"` (passes `validateBundles`: `parseDetent` accepts any k>0, `c` is unbounded, no `frames_max` is declared so the on-detent cap check at schema.ts is skipped), `framesMax` returns `-100`.
- Trigger: hand-edit bundles.json with `constraints.frames: "1000n+900"`, `frames_max` absent, `defaults.frames: 900`; reload. Boot coercion (bundlesStore.ts line 141) runs `coerceParams`: line 85 snaps 900 -> 900 (on-detent), then line 87 clamps `900 > -100` -> seats `frames = -100`.
- Impact: the bundle is permanently unusable — `violations()` reports "frames must be a positive number." (line 119) for a value `coerceParams` itself wrote, and `buildWorkflow` (fill.ts line 83-84) throws on every render. No crash, no bad render escapes (the gate holds); the failure is a self-inflicted, misleading state whose spoken message names the symptom, not the culprit detent.
- Fix: in `framesMax`, floor onto the detent but never below the smallest positive on-detent value (e.g. take `Math.max(computed, snapToDetent(1, det))` or reject the detent outright); better, add the schema twin — validate that a declared detent admits at least one positive value under the ceiling (bound `c` or require `snapToDetent(521-floor, det) > 0`). CONFIRMED by tracing the full chain (schema accepts -> boot coercion seats -100 -> violations refuse -> buildWorkflow throws).

Draft findings refuted and dropped in Phase 3: off-detent declared `frames_max` seating an illegal count (schema.ts enforces `snapToDetent(frames_max) === frames_max` when a detent exists — the gate-round-2 check); `width_multiple: 0` making `width % 0` always-truthy (schema requires positive integer, and the store only accepts validated files); `steps_min > steps_max` making `coerceParams` seat a step count that `violations()` always rejects (schema enforces ordering plus defaults-in-bounds); `frames`-snap message misattribution when the cap binds (bundlesStore setParam speaks its own cap message at its line 246-248 alongside the detent snap, both true of the settled value).

## Missing safeguards
- `validateBundles` never checks that a frames detent admits any positive value under the effective ceiling (nor bounds `c`), which is what makes the LOW finding above reachable — the two implementations of "what frames are legal" agree, but neither states the legal set is non-empty.
- `snapToMultiple` has no guard against `m <= 0` (division by zero -> `Infinity` via `Math.max`); every current caller is shielded by the `> 1` guards at lines 88-89 and schema's positive-integer rule, but the export's own contract ("never below one multiple") is only enforced by convention.

context-pack: delta = e7bc621 only; new accessors + coerceParams + expanded violations/snapMessage, twin-checked against schema.ts validation, consumers traced in bundlesStore.ts (boot 141/182/315, setParam 246), fill.ts:83 (build-time throw), GenerateSurface.tsx:52; schema closes the off-detent-cap, zero-multiple, and min>max doors, leaving one negative-fallback edge.
new-findings: 1
