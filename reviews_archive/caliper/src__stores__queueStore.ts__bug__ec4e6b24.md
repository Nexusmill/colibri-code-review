# colibri bug review - src/stores/queueStore.ts (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 ec4e6b24 - 2026-08-25
mode: bug (delta on 0aec9a4c, 2026-08-19) - context: 14 importers (App, DeckControls, ScreenStage, surfaces, assetsStore); ws event semantics re-traced; reconnect reconciliation and clearAll/cancel terminal-state guards followed

## Verdict

Shippable - the delta is clean.

## Fixed since last review

- [OLD LOW] Duplicate rejected-job ids from Date.now() alone: FIXED - `rejected-${Date.now()}-${++rejectSeq}` (line 116).

## New findings

None confirmed. Re-verified: the queueInFlight TOCTOU guard across the queuePrompt round-trip; executed-events accumulating before the terminal executing(null); late/duplicate event resurrection guards; the reconnect reconcile against getLiveQueueIds. The unguarded `executed` output-append on a terminal job is truthful (the files exist server-side) and idempotent in effect on pickFiles consumers.

## Missing safeguards

- randomSeed's 48-bit range slightly exceeds the seed ScrubInput max (2^47) - unreachable-by-scrub display range only, no functional effect.
