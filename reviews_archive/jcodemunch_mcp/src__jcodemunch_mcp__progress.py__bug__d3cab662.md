# Colibri review — src/jcodemunch_mcp/progress.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\progress.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `d3cab662695c5d04caebec1c7ba36feb712bb1207ab5adfc44927a25b753fc0b` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 3 refuted); `_heartbeat_interval` 63-78 (`float(raw)` with only ValueError caught), `HeartbeatReporter` 241-290 (`enabled = interval > 0`, `if now - self._last_emit < self._interval`); the docstring's own rule: garbage parses to the default rather than disabling, because the failure this exists to fix is silence. No prior `.colibri_reviews` record.

## Verdict
`float()` accepts `nan` and `inf`, and the parser trusted it: nan compared false against every elapsed time (a heartbeat on every tick), inf never elapsed (permanent silence - the very failure the heartbeat exists to prevent). Fixed: non-finite is garbage, and garbage means the default.

## Bugs & vulnerabilities
**[MEDIUM] Non-finite `JCODEMUNCH_HEARTBEAT_SECONDS` accepted — CONFIRMED — FIXED** - `line 73-77`
- Trigger (audit probe, RED on these bytes): `JCODEMUNCH_HEARTBEAT_SECONDS=nan` → 50 heartbeat lines inside the first interval; `inf` → none, ever.
- Fix: `math.isfinite` after the parse; nan/±inf log at debug and return the default. `<= 0` is deliberately untouched - `enabled = interval > 0` makes it the documented explicit off switch.

## Refuted (recorded so they are not re-raised)
- `_send` double-appending under concurrency, `drain_reporter` hanging past timeout, negative bar width: all three re-traced by the sub-agent and stand refuted.

## Adversarial verification (Phase 3)
- Pinned on `_heartbeat_interval` for `nan`, `inf`, `-inf`, `NaN`, `Infinity`; controls pin `2.5`, `0` (off), `banana` (default) and unset (default).

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `dbda237599ce437a8200eaf86f0658c3567cd7371371370537657ae9896eec04`. TDD: `tests/test_tail_batch1_reaudit.py` (16 tests across the three units of this batch) - 13 RED on the old bytes, 3 controls green throughout, GREEN after; the audit probe passes after.
