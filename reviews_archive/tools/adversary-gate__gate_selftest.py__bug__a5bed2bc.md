# Colibri delta review

Source: adversary-gate/gate_selftest.py
Reviewer: Codex (in-session)
SHA256: a5bed2bcbf06731afbef1b0b83381ce577462c5530a9554375360e098718c675
Date: 2026-09-27
Mode: bug
Context: canonical Tools history, marketplace byte parity, pre-write findings, snapshot call sites, ReviewedWriter and regression tests.

## Fixed since last review

Added regression execution of the real snapshot function with isolated Git/provider effects. Tests catch eager reads and an unlocked evidence fallback. Explicit branches preserve assertions under optimized Python. Existing payload ordering and omission checks remain.

## Verdict

No further confirmed finding in this change. Independent Luna pre-write CLEAR retained in the paired sync artifact.

## Cross-file synthesis

Canonical Tools owns these repairs; marketplace ships only its established gate payload. The broker stays Tools-owned. Colibri evidence references are repaired through the bounded broker and committed separately.

Follow-up: inherited Jev promotion fixture reproduced a small-payload failure. Both deterministic routing fixtures now explicitly disable Jev; targeted e2e cases pass. Full gate suite194/194 passed before this two-line fixture isolation, with the affected cases rerun afterward.

Final alignment delta: forced text diffs preserve oversized source marked -diff; actual binary gated files and removed binary gated files are refused before review. Real Git260KB fixtures were RED before, GREEN after. Bracket-name regression invokes production artifact writer and adjudication parser, and passes. Contextual factual rebuttal retained against the incorrect relative-path allegation; production uses basename matching.

Final base-side correction: check frozen base for every emitted code path, preventing binary-to-text same-path exposure. Actual transition was RED before correction. Rename concern rebutted using actual R099 Git fixture: literal destination-only pathspec emits added destination content from /dev/null, with old binary marker absent.

Follow-up confirmed findings: corrupt adjudication JSON and staged-shas writers must preserve original evidence instead of resetting. Three malformed-evidence tests observed RED then GREEN after raising on parse corruption. Local latest-artifact helper now orders timestamp/suffix numerically; suffix2/10 fixture observed RED then GREEN. Independent exact-byte prewrites CLEAR for both files.
