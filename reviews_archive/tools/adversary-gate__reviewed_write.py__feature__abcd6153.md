# adversary-gate/reviewed_write.py - feature review

source: C:\Users\User\source\repos\Tools\adversary-gate\reviewed_write.py
reviewer: in-session GLM-5.3 (ZCode) · sha256: abcd6153cee72611f9453d785583bfe28427f3a8fdf1783013f1baaced51e18b · 2026-10-08 17:46 · mode: feature
context pack: full-source read this session (F18/F22 remediation); caller = the universal-tools safe_write MCP path agents use for every repo write; gate interop via gate._call_model/gate._scrub_text; no prior feature rows.

## What this module does

The canonical pre-write review broker: an exact-byte before/after proposal for a
dangerous write is independently reviewed by the strong rung (gate.TIER2_CHAIN),
evidence artifacts (attempt log, scrubbed block reason) are persisted, and only a
CLEAR authorizes the write; every other outcome refuses with durable evidence.

## Suggested add-ons

- **WARN-specific denial guidance** — Value HIGH · Effort S
  What: when the strong rung returns WARN (LOW-only findings), the WriteDenied
  message says so explicitly: "LOW findings recorded (see evidence); address or
  re-propose" instead of the generic refusal text.
  Why: F22 made the evidence honest, but the caller-facing message still reads as
  an unqualified BLOCK — agents then treat LOW findings as hard failures and burn
  rebuttal cycles on noise.
  How: branch the `raise WriteDenied` on `outcome == "WARN"`; the outcome string
  is already in scope. Hook: the `if not clear:` block.

- **Pre-write denial adjudication feed** — Value MED · Effort M
  What: feed pre-write BLOCK/WARN episodes into the same
  `.adversary/adjudications.json` true-rate store the commit gate uses (new
  episode type "pre-write").
  Why: two ledgers exist today — commit denials are adjudicated, pre-write
  denials are not; the owner's true-rate picture is blind to half the gate's
  catches (the earliest ones, before bytes ever stage).
  How: `_append_adjudication` is importable; stamp a row in `write()` when a
  review refuses. Hook: after the evidence artifact lands.

- **Proposal coalescing for multi-file writes** — Value MED · Effort M
  What: an API to batch N file proposals into ONE review payload (one paid round
  instead of N) with per-file verdict rows in the evidence.
  Why: an agent tranche touching 5 files pays 5 strong-rung reviews of nearly
  identical prefixes; one payload preserves the cache and cuts cost ~N×.
  How: extend the payload builder to concatenate per-file sections; per-file
  verdicts parsed from the findings' file citations. Hook: `ReviewedWriter.write`
  gains a `batch()` sibling.

## Nice-to-haves

A `--why` read-out on the evidence artifact path (today callers must open the
JSON); usage/cost echo in the evidence row (usage is already returned); a
metrics counter (proposals/refused/warned) for the fleet dashboard.
