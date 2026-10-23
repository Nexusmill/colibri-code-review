# plugin/hooks/protocol-gate.mjs - debug (green-run stamping)

- source: `plugin/hooks/protocol-gate.mjs` · model: claude-fable-5-1 (in-session) · mode: debug · date: 2026-09-08T13:13:03+00:00
- sha256 reviewed: `630c77526e6b1b811f062a2bef2d9e311ff6c63d76221e0342b5ea200da9bf81` (62c4bcc bytes) · after fix: `ac3a86a8fc0d47b6524723c00c268bc9cf351f38aced9c272bf587f6de06f42c`
- context pack: the stamp consumer at the commit leg (`verifyTs` fresh within 45 min, line ~240); the
  runner-shaped source rule (round 22) and GREEN-ONLY exclusion (round 4) at lines 80-94; the hook
  battery `skill-gate-selftest.mjs` rows 326-339 (heredoc / inline / runner stamping); recent history:
  the other session's 62c4bcc "sixteen rounds" landed the plugin hooks after this defect class was
  first flagged from a shared-index gate run on 2026-09-07 (gate_20260907-211007, memory handoff).

## Reproduce
Owner order 2026-09-08: "go ahead with the tools fix but scan tools before you do, make sure it still
needs it". A node probe of the CURRENT exclusion `/\bfailed\b|\bFAIL\b|exit code [1-9]/` plus the
stamp shapes against runner outputs:

| output | stamps |
|---|---|
| vitest mixed `Tests 2 failed \| 26 passed (28)` | no (fixed by round 4) |
| jest / pytest mixed | no |
| vitest errors-only `Tests 2 passed (2)` + `Errors 1 error` (exit 1) | **yes** |
| `26 passed (26)` + `Exit code 1` | **yes** |
| clean vitest, harness green | yes |

## Hypothesis ledger
1. The flagged class (mixed summary credited) is already fixed - CONFIRMED by the probe:
   **verified-stale**, not re-fixed.
2. The exclusion omits a nonzero ERROR count, so vitest's unhandled-error run (all tests pass,
   `Errors N error`, exit 1) stamps - CONFIRMED (probe + battery row RED).
3. The exit-code clause is lowercase-only, so an `Exit code 1` trailer never vetoes - CONFIRMED
   (battery row RED). Whether the hook ever sees that trailer in `tool_response` is unverified;
   the clause exists, so it must at least work.

## Fix (one line, root cause)
Exclusion becomes `/\bfailed\b|\bFAIL\b|\b[1-9]\d* errors?\b|[Ee]xit code [1-9]/`. The fail
words stay case-sensitive on purpose: `/FAIL/i` would match the `0 fail` of bun's green summary
and un-stamp a passing run. `0 errors` (tsc) does not veto.

## Verify
Battery rows added (RED first): `verifystamp_mixed_summary_not_stamped` (pins round 4),
`verifystamp_errors_only_red_not_stamped`, `verifystamp_exit_code_trailer_not_stamped`,
`verifystamp_zero_errors_still_stamps`. RED: 2 fail. GREEN after the fix: 106/106.

## Not changed
The runner-shaped source rule, the inline-code exclusion, the stamp shapes, the 45-minute window.
