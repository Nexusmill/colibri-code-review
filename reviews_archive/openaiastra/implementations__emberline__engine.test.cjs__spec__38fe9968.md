# Independent engine review

Source: C:/Users/User/source/repos/OpenAIAstra/work/docking/engine.test.cjs
Target: implementations/emberline/engine.test.cjs
Reviewer: GPT-6 Codex agent /root/dock_music (not engine author)
SHA-256: 38fe996851be6a07df7216a5e46c8d9382d2984159fc0ba6bc4f5b6f94f245eb
Date: 2026-09-08
Mode: spec
Context: current task docking/music plan; GUARDRAILS, state, activity, remediation/features/deferred; native JCodemunch engine outline and game.frame call site; recent engine commits d897fad, 058a90b, 974c990; current complete candidate bytes and diff.

## Verdict

CLEAR for these exact bytes and reviewed scope. No confirmed divergence from the authoritative docking/guardian clauses.

## Review evidence

Reviewed all 119 current lines. New guardian tests at 104-119 assert actual lives lost within 1.5 seconds, an independently bounded 0.35-0.45 warning interval, fixed footprint while escaping, and repeated damage with bounded growth. The earlier five-second assertion changes to the intentionally requested 1.5-second behavior. Fixtures disable unrelated spawning, and the long-pressure fixture explicitly supplies 100 lives to permit observing multiple real hits. No implementation-derived expected timing constants. Existing campaign/FIFO/save/motion/combat tests preserved.

## Divergences

None found. Candidates were challenged against current call order, state initialization, preexisting station rules, and fresh runtime checks.

## UNJUDGEABLE HERE

Human full-campaign balance, audiovisual rendering, and UI mute/visibility behavior require UI/browser acceptance. No claim of ordinary dodge success in all four vehicle modes; the new test exercises opening flight.

## Validation

Independently ran node --test work/docking/engine.test.cjs work/docking/spectrum.test.cjs: 82 tests, 82 pass, zero failures. Exact candidate SHA-256 verified against author manifest. Production not modified; this is pre-write review evidence, not the additional armed Git review/notary.
