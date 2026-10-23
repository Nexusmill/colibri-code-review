# Colibri delta review

Source: adversary-gate/adversary_gate.py
Reviewer: Codex (in-session)
SHA256: b520a143265aa08f1196e5d2f68450e687ed57af892e77a13e8d555f74a3dff6
Date: 2026-09-27
Mode: bug
Context: canonical Tools history, marketplace byte parity, pre-write findings, snapshot call sites, ReviewedWriter and regression tests.

## Fixed since last review

Confirmed eager staged-blob memory retention; changed the list to an ordered generator. Confirmed unlocked fallback evidence race; artifact persistence failure now returns failure without clearance. Existing durable-partial-artifact handling retained. Both actual snapshot regressions failed before their fixes and passed afterward. Model chain remains owner-selected. Adjudication append loss is the documented loud degraded contract, not silently claimed recovery.

## Verdict

No further confirmed finding in this change. Independent Luna pre-write CLEAR retained in the paired sync artifact.

## Cross-file synthesis

Canonical Tools owns these repairs; marketplace ships only its established gate payload. The broker stays Tools-owned. Colibri evidence references are repaired through the bounded broker and committed separately.

Final alignment delta: forced text diffs preserve oversized source marked -diff; actual binary gated files and removed binary gated files are refused before review. Real Git260KB fixtures were RED before, GREEN after. Bracket-name regression invokes production artifact writer and adjudication parser, and passes. Contextual factual rebuttal retained against the incorrect relative-path allegation; production uses basename matching.

Final base-side correction: check frozen base for every emitted code path, preventing binary-to-text same-path exposure. Actual transition was RED before correction. Rename concern rebutted using actual R099 Git fixture: literal destination-only pathspec emits added destination content from /dev/null, with old binary marker absent.

Follow-up confirmed findings: corrupt adjudication JSON and staged-shas writers must preserve original evidence instead of resetting. Three malformed-evidence tests observed RED then GREEN after raising on parse corruption. Local latest-artifact helper now orders timestamp/suffix numerically; suffix2/10 fixture observed RED then GREEN. Independent exact-byte prewrites CLEAR for both files.
