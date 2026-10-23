# colibri feature review - colibri-bounty/tests/test_p2_units.py

- source: `colibri-bounty/tests/test_p2_units.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `e9168668018afe29824271f67ec844e59eccb493c0528ebfdde2be74493fda81`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0337 (in=3345 out=4507)

## grok-4.7 output (verbatim)

## What this module does

This suite locks the P2.2 packing contract: `p2_units.cluster_files` groups a provided Solidity file list into units by live cross-references (imports and type uses), ignores commented mentions, and splits only on a raw-text char budget while still covering every file exactly once (an oversized file stays its own unit). It also pins that `replay --run p2x` is an accepted CLI choice, so that packer is a real offline replay path rather than a dead branch. Measurement stays free and deterministic; nothing here spends on a live contest.

## Suggested add-ons

**1. Affinity-preserving split under the char cap**
Value: High
Effort: M
What: When a reference-cluster exceeds the budget, cut the weakest edges first so an import/type pair stays together unless that pair alone is over cap. Keep the existing exactly-once coverage and the singleton-oversized rule.
Why it helps the user: P2.2 exists so the auditor sees integration in-unit. A size-only split can put `A.sol` and the `B.sol` it calls in different units, which shows up later as a miss that is really a packing miss. Preserving edges raises the chance cross-contract findings are even visible to the tier, without changing denominators.
How: Extend the split path inside `p2_units.cluster_files` (the path `test_char_cap_splits_but_covers_every_file_exactly_once` already asserts). Default budget stays `p2_units.DEFAULT_UNIT_CHARS`; do not add a dependency.

**2. Path-shaped import clustering for real contest trees**
Value: High
Effort: M
What: Resolve import specifiers against the file list actually passed in (`./B.sol`, `../src/B.sol`, `src/B.sol`), not only same-directory basenames, and still refuse to link names that appear only in comments.
Why it helps the user: Replay runs against the corpus, which is not a flat tmp tree. Basename-only edges under-cluster Foundry layouts, so related contracts are audited apart and P2.2 precision/recall is not like-for-like with how those contests were written.
How: Extend the reference walk used by `p2_units.cluster_files`. Keep the no-edge behavior pinned by `test_commented_references_do_not_link`. Wire the same file list `cli.cmd_replay` already builds for `--run p2x`; no corpus walker and no new runtime deps.

**3. Offline unit manifest on the p2x replay path**
Value: Med
Effort: S
What: For a p2x replay, write a small manifest per unit: member paths, raw char count, budget used (`DEFAULT_UNIT_CHARS` or the override), and whether the unit is a forced singleton over cap. Surface a one-line summary from status.
Why it helps the user: Clustering is currently invisible outside pytest. An operator cannot tell a model miss from "these two files were never co-located," which breaks the honest-measurement rule that contamination and denominators stay disclosed. The manifest is free, offline, and does not merge agent-tier figures with the union.
How: Have `cli.cmd_replay` record the list returned by `p2_units.cluster_files` on the p2x branch (`test_p2x_is_a_reachable_run_choice` already proves that choice parses). Let `cli.cmd_status` print unit count and raw-chars vs `p2_units.DEFAULT_UNIT_CHARS`. Leave `adjudicator=None` and do not call a paid channel.

## Nice-to-haves

- Stable unit ordering from `cluster_files` so two replays of the same tree diff cleanly in the manifest.
- `cli.cmd_status` headroom line: raw unit chars versus the known raw-text truncation ceiling, using the same raw measure as `test_packing_budget_measures_raw_text`.
- Optional org prefix filter via `cli.ORGS` so a status/replay manifest can be scoped to one mirrored tree from `cli.cmd_mirrors` without a second packer.

- ACCEPT affinity-preserving split under the char cap (weakest edges cut first) - test-side twin of p2_units hub-preserving suggestion; module packing verified size-only.
- ACCEPT path-shaped import resolution (./B.sol, ../src/B.sol vs basename-only) - VERIFIED: the module links on g.name == rel only; corpus trees are not flat.
- ACCEPT offline unit manifest on the p2x replay path (members, chars, budget, forced-singleton flag) - clustering invisible outside pytest today.
- DEFER nice-to-haves (empty-tree pins, tie-break pin - per file's own list).
