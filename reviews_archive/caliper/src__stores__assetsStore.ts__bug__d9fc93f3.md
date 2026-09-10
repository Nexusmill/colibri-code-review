# colibri bug review - src/stores/assetsStore.ts (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 d9fc93f3 - 2026-08-26
mode: bug (delta on 26bfa703, 2026-08-19) - context: consumers Library/Outputs merge paths; the 2026-08-25 StrictMode double-hydrate fix in the file

## Verdict

Shippable - the delta is clean.

## New findings

None confirmed. The single-flight hydrate (hydrateInFlight memo with finally-clear), the transient-server-away retry (records left unmarked), and the sync-not-append merge against the current provenance list all hold. pickFiles' role detection matches every producer's extensions.

## Missing safeguards

- `dismissed` grows unboundedly within a session - bounded in practice by deletions per session.
