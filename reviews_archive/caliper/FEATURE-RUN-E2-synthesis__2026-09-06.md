# E-2 synthesis - key liveness + stale routes (2026-09-06)

Cross-file chain: PROBES table + probeVerdict (pure, grounded urls) ->
vite.keys.ts /test (server-side key walk, Bearer, 10s timeout) -> testKey
client -> SettingsConsole row chip states; stale detection reads the same
getCloudModels the picker uses, flag-only (resolution stays server-side -
the R1 client-guessing pattern was considered and rejected for anything
that decides what runs).

Ranked findings across files:
1. [FIXED in-pass] OpenRouter's default key label IS truncated key material - rendered like a leak; labels starting sk-or- no longer display (test-pinned).
2. [FIXED in-pass] CLEAR test clicked the row's first button - TEST now precedes CLEAR; selects by text.
3. [FIXED in-pass] two TypeScript annotations crashed the .mjs harness at module load (node --check joins the wave discipline).
4. [LOW, accepted] spacexai probes an undocumented models endpoint; 404 degrades to "endpoint away", never a guessed dead key.
5. [LOW, accepted] account strings render via React textContent/attributes - escaped, no injection path.

Live evidence: HF live (Dosb5912), Replicate live (phantom-man), OpenRouter
live; probe slug flagged GONE FROM CATALOG in the real window with the
owner's route restored and re-read; tier 61/0/4 exit 0; vitest 449/449.

## Adversary round 1 (BLOCK) - both findings fixed at the root
1. [MEDIUM, FIXED] a stored verdict survived key replacement - save() drops
   the row's verdict on every set/clear; regression test pins the
   probe-DEAD -> clear -> paste -> save -> chip-SAVED flow.
2. [LOW, FIXED] stale flags never cleared for types leaving the cloud set -
   the effect resets them; regression test pins local-switch clearing the
   danger register. The dead service:type dedupe folded into the reset.

## Adversary round 2 (BLOCK) - all three findings fixed at the root
1. [MEDIUM, FIXED] in-flight probe re-attaching to replaced key material -
   generation counters in runTest/save; deferred-promise regression test.
2. [MEDIUM, FIXED] late catalog fetch overwriting the newer route state -
   alive guard on the effect; deferred-catalog regression test through the
   picker's real onClose refetch path (the gate also rejected my earlier
   fresh-mount test as trivial - correctly).
3. [MEDIUM/FIXED as part of 2] danger styling gated on the route being
   cloud, beside routeText's own branch.
Final: tsc 0, vitest 452/452, build 0, tier re-run post-fix.
