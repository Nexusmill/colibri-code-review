# Colibri playability debug: gardens.js

Source: implementations/emberline/gardens.js
Reviewer: Codex /root, in-session
SHA-256: 1528409fe0857ccb3a3ccbba39dbb231ede589ec23b5a5e790f76b71b91edba0
Date: 2026-09-30 06:41 America/Denver
Mode: bug (focused debug modality)
Context: current-byte native reads, jCodemunch source/call paths, owner report, required state/guardrails/feature/remediation/deferred records, prior per-file report, test-first failures and final native checks. See docs/tasks/2026-09-30-emberline-playability.md for cross-file synthesis.

## Verdict
The first region now has a lower introductory target and a bounded ramp; original stages6–50 are preserved. Human difficulty remains a playtest judgment.

## Bugs and vulnerabilities
CLOSED, MEDIUM product-fit issue: the original first target60000 required at least ten full eight-ember deliveries. Owner reported being unable to leave level1. Final targets1–5 are9600,22400,35200,48000,60800;6–50 keep original68000–136000. Three six-ember banks clear the first garden; two do not.

## Fixed since last review
Prior feature review3583a896 proposed progress presentation, which this task does not reopen. Only target generation changes. Shared encounter rules, stage IDs, ordering and assigned vehicles remain unchanged.

## Adversarial verification
An initial first-only reduction was rejected because it left an immediate61000 second-stage wall. A provisional all-campaign shallow curve failed real replay pacing. The final test pins all50values as an independent literal catalogue. Replay across seeds1/2/3 permits at most the introductory clear in30seconds and fewer than five clears in120seconds. A provisional minimum10second intro duration was removed after an efficient seed legitimately cleared sooner; no owner minimum-time requirement existed. Final source checks37tests/5skips/exit0,60.862s,unchanged tree, include the actual bank progression and route assertions. Independent final source CLEAR e105f6d9196345e7a4e0efb36231a4af.

## Missing safeguards
Automated routes do not establish human retention or difficulty. Await owner play feedback on the lower opening target.
