# E-1 synthesis - node self-identification (2026-09-06)

Cross-file chain, one direction of truth: python payload `node` (installed
copy's version + own-file sha) -> CaliperVram.node (types.ts) -> nodeSyncVerdict
(pure, tested) -> footer line (dim in-sync / danger drift / pre-self-id) with
/api/node-sync (repo canonical, hashed server-side) as the comparison's other
half. Consumer audit: vite.agent.ts, preflight.ts, tools.ts summarizeVram all
read OTHER fields of the payload - additive change, no breakage (verified by
full vitest 438/438 + tier 59/0/4).

Ranked findings across files:
1. [LOW, accepted] empty self-sha would read as drift, not unknown (near-unreachable path).
2. [LOW, accepted] /api/node-sync is method-agnostic (idiom-consistent, read-only).
3. [FIXED in-pass] harness log honesty (three-way backend/node/away) + manifest id parity (gate caught it).

The feature's own guarantee verified end to end live: canonical sha f2dbb57b
== deployed sha (both copies re-hashed this session), payload carries it through
the running backend, footer renders "node v1.1.0 - in sync", harness compares
the pair on every fast tier. Drift now announces itself instead of being
hand-believed.
