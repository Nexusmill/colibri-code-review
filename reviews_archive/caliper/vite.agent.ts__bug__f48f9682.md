# colibri bug review - vite.agent.ts (delta)

source: vite.agent.ts · reviewer: ZCode GLM-5.3 in-session · sha256 f48f9682 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 663172ab @ af12a90 2026-08-22; unchanged regions byte-identical to prior sha)
context: diff 29+10; prior review 663172ab (zero confirmed) carried; cross-file: COMFY_URL, tools.ts filterNoopProposals (cache-hit at 84daa792), the no-op filter's new input order traced both divergence cases (manual live flag / config-only flag).

## Verdict

Shippable - no new defects; two prior asymmetries fixed in this delta.

## Bugs & vulnerabilities

None new. The currentState spread-order flip (live server flags now override config) is a deliberate semantic matching the owner's live-truth doctrine (apply reports against the running server's own argv): traced both divergence cases - config-only flags still surface (live spread cannot remove keys); a manual live-only flag now makes a matching proposal read as the no-op it observably is (the persist-to-config edge is accepted by that doctrine).

## Missing safeguards

- caliper.config.json read-modify-write remains last-write-wins across concurrent applies (prior, theoretical single-user).

## Fixed since last review

- The bench-call asymmetry (reachable applyProposal fallthrough instead of an explicit skip) - FIXED: bench now joins read_kb in the proposal-exclusion set, and narrated bench calls no longer render a clickable "unknown action".
- (bonus fixes in delta) no-op filter now owns the zero-calls exit too; sidecar usage tokens accumulate instead of reporting zeros; tool_calls gain the type discriminator for cloud-brain shape parity.

## Verified-correct (adversarial passes, findings deleted)

- Sidecar usage accumulation arithmetic (+= on both token fields, absent-usage default 0); the values[0]/[1] cast is typing-only (validateToolCall already enforced the tuple).
