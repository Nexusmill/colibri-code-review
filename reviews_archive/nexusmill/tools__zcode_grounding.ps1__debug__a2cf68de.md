# Debug record - tools/zcode_grounding.ps1 (ZCode SessionStart grounding hook)

- source: tools/zcode_grounding.ps1
- sha256 (post-fix, final): aed27202d2de247b1309bd85e3d176a755ffb1ee63fb8d0fa0a985ae9967664a
- sha256 (post-fix, gate round 0): a2cf68deaa6d8e5336efe835c96854312718d66a863db890e9f34841e827b270
- sha256 (pre-fix, merged bytes): 5e89484451f22a1aad716c6c902e13c37c9767b6a40321383f9433a277f012cb
- date: 2026-10-24
- mode: debug (Phase D) - merge-integration defect caught by the merged hook suite
- model: deepseek-v4.1-flash (in-session)
- prompt: colibri/local-reviewer@1 (cache)
- context pack: jcodemunch file outline; .zcode/config.json (hook wiring) + tests/test_zcode_hooks.py (the contract source - _assert_contract's 10k cap); docs/remediation_manifest.json consult (no prior finding for this file); RSI rules query (0 applicable, lang=ps1); sibling audit - tools/session_grounding_hook.ps1 (Claude twin): no front/board blocks (0 mentions), fixed ~7500 slice, no total-budget machinery -> adjudicated not-applicable; colibri store consult: no prior row for this file (the twin's 2026-09-03 HOOK-JSON-CODEPAGE debug record read as context).

## Reproduce (RED)
Merged suite run 1 (junk/merge_12h/suite_run1.txt): 7 failed, 83 passed. All 7 = FrontRegistryWiringTests._assert_contract rows asserting len(additionalContext) <= 10000; measured 10040 / 10044 / 10129 / 10196 / 10208 / 10519 / 10547.

## Hypotheses (ranked; checked against source)
1. CONFIRMED - the autoland T1.2/T2.2 front/board notes append to $ctx AFTER the snapshot slice; ``$cap = 10000 - $ctx.Length - $snapHeader.Length - 6`` was computed before those appends, so the notes rode outside the budget. Overflow equals the note length exactly (10,000 + note length = every observed value).
2. REFUTED - the snapshot slice itself mis-sized: the local line ran green with the same slice machinery; the delta is exactly the appended notes.
3. REFUTED - test-environment artifact: the overflow scales with the note text (occupied/astral rows largest), not with the fixture.

## Fix (round 0)
Pure reorder (junk/merge_12h/fix_grounding.py, every anchor count-asserted): the front/board blocks are built BEFORE the snapshot section, so they are already in $ctx when $cap computes and the snapshot (the flexible, least-lossy element) absorbs their length by construction. Block logic untouched; comment edits record the merge decision. Output order: stats -> notes -> snapshot LAST - which also restores the directive's own "the AGENT_STATE START-HERE snapshot is LAST" contract and keeps the OCCUPIED front warning out of display-truncation range.

## Verify (round 0, GREEN)
Merged suite run 2 (junk/merge_12h/suite_run2.txt): 90 passed in 158.35s. Parse check: PARSE OK. Installed bytes byte-identical to the built file (safe-edit sha_after a2cf68de...).

## Gate round 1 (adversary pre-commit, deepseek/deepseek-v4.1-flash-1017@deepinfra) - BLOCK, both findings real
1. MEDIUM (tools/zcode_grounding.ps1): the slice's ``[Math]::Max(200, $take - 74)`` floor still ignored $cap - safe only while $ctx stayed under ~9.66k (guaranteed pre-merge; the notes now ride $ctx, whose ceiling is ~10.7k with health/ingest at their caps). In the floor branch the payload overflowed by up to ~270. CLOSED by construction (junk/merge_12h/fix2_grounding.py): (a) a NOTES BUDGET GUARD clamps the notes to the remaining budget before appending (ctx <= 9850 + 4 separator chars; board digest yields first, then the front note keeps its verdict prefix with the file's established surrogate guard); (b) the take floor yields to $cap (``[Math]::Max(0, $cap - 74)``); (c) the truncation marker appends only when it fits. Invariant re-derived for every branch: marked path snapshot <= cap - 4 (total <= 9994); unmarked path <= cap (total <= 9998); the 10k contract holds with 2 chars of worst-case headroom. Not hermetically testable today: reaching the branch needs ctx > 9.65k, and health/ingest are registry/store-driven with no env seam (verified: health_ledger.py has only REPO_HEALTH_BUDGET, summary_ingest.py reads a fixed repos.json) - the closure is arithmetic, re-checkable against the bytes.
2. LOW (tests/test_zcode_hooks.py): test_grounding_board_failure_fails_open asserted "AUTOBOARD: unavailable" unconditionally - on a pip -e/.pth machine the bogus NEXUSMILL_BOARD_TOOLS still resolves, the digest runs against live state, and the row false-reds. FIXED mirroring the front row's environment-agnostic pattern (either outcome valid, ctx[-300:] in the message).

## Gate round 2 (tier-2 qwen3.8-omni-flash, WARN)
Verified the fix against the bytes (the contract holds; the 7-row regression net is real; both manifest rows are canonical; the stop-gate heartbeat ordering is right; the guard comment matches the live tests) and found one informational LOW: the stated bound was imprecise - 9994 is the MARKED path; the unmarked slice path reaches 9998 (2-char headroom) and the missing-state path 9965. No runtime violation; corrected in the file comment + both manifest texts + this record, same session.

## Verify (final, GREEN)
Merged suite run 3 (junk/merge_12h/suite_run3.txt): 90 passed in 166.01s. Parse check: PARSE OK (both installs). Installed bytes byte-identical (safe-edit sha_after aed27202...).

## Finding contract (CONFIRMED)
- verbatim snippet (pre-fix): ``$cap = 10000 - $ctx.Length - $snapHeader.Length - 6`` and, later, ``if ($front_note) { $ctx = $ctx + "`n`n" + $front_note }``
- concrete trigger input: any SessionStart with the front claim active (the default path - every real session)
- producing caller: .zcode/config.json hooks.events.SessionStart -> tools/zcode_grounding.ps1
- broken behavior: additionalContext exceeds 10000 by the notes' length (consumer cap; display truncation eats the tail - including the OCCUPIED front warning)

## Residual (recorded, not fixed here)
None open in the budget path: every branch is bounded by construction (notes guard + slice yield + conditional marker). If the health/ingest caps are ever raised, the NOTES BUDGET GUARD bound must be re-derived (stated in the file comment).
