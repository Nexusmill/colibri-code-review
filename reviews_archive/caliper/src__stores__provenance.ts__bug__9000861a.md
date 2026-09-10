# colibri bug review - src/stores/provenance.ts (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 9000861a - 2026-08-26
mode: bug (delta on 1e5805b7, 2026-08-19) - context: callers queueStore (save at queue, patch at terminal), Library mount (refreshProvenance + hydrate), OutputsSurface; server route /api/provenance contract

## Verdict

Shippable - the delta is clean.

## New findings

None confirmed. The server-is-truth hydrate (no legacy merge-back, the 2026-08-22 deleted-fixture lesson), the 200-cap newest-first cache, remove-then-persist atomicity of intent, and the reference-equality patch guard all hold.

## Missing safeguards

- refreshProvenance during an in-flight patchProvenanceOutputs can overwrite the cache with a pre-patch server snapshot (PUT still lands; next refresh self-heals) - a narrow mount-vs-completion race, noted.
