# colibri bug review - src/bundles/constraints.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 bd427237 - 2026-08-25
mode: bug - context: 8 importers (schema, DeckControls, ScrubInput, bundlesStore, queueStore, GenerateSurface, fill.ts), constraints.test.ts green, parseDetent regex traced against schema.ts's load-time validation

## Verdict

Shippable after the one fix below. Small, load-bearing, clean.

## Fixed since this review (same session)

- [LOW] violations() and snapMessage() hardcoded "Frames must be 8n+1." while the detent is per-bundle configurable (`constraints.frames`) - a bundle with e.g. 16n+1 would show a lying message, against the owner's truthful-status rule. FIX: both messages interpolate b.constraints.frames. Byte-identical output for every current bundle (all 8n+1) - no visual change ships.

## Missing safeguards

- snapToDetent rounds to nearest n including n=0 (frames=1 for 8n+1) - valid by design; no guard against pathological k (k>0 enforced at parse).

## Verified-correct (adversarial passes, findings deleted)

- NaN cfg skips the cfg branch but is caught by the generic NaN/<=0 sweep; seed exempted deliberately; cfg_max===1 pinning including 1.0; parseDetent rejects leading + and k<=0.
