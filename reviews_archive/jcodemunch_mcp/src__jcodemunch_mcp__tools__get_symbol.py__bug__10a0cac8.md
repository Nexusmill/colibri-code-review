# Colibri review — src/jcodemunch_mcp/tools/get_symbol.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_symbol.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `10a0cac856ae741dfbcd488328d2af33a0587a517c7cfb66d6e4e693cd7d74c3` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 0 refuted; one unpursued note); `get_symbol_source` 367-743 - `verify_against` compared with `== "git_sha"` at each use and never validated, so any other string ran the cache path; the bounds validation block 431-… (the pattern to match); `_verify_against_git_sha` 140-295. No prior `.colibri_reviews` record.

## Verdict
A caller who asked for the externally-attested comparison with a misspelt mode got the weaker cache-only check with no sign. Fixed: an unknown mode is an error, validated up front like the bounds.

## Bugs & vulnerabilities
**[MEDIUM] Unrecognised `verify_against` silently degraded to cache-only verification — CONFIRMED — FIXED** - `line 429`
- Trigger (audit probe, RED on these bytes): `verify_against="git-sha"` → no error, no `git_sha_verification` block.
- Fix: `verify_against not in ("cache", "git_sha")` → `{"error": "Invalid verify_against … Must be 'cache' … or 'git_sha' …"}` before any work, in the same up-front style as the source-bound validation.

## Noted, not pursued (from the sub-agent; not confirmed)
- `symbol['file']` interpolated into a git revspec argument in `_verify_against_git_sha` (list argv, no shell; a path is an indexed relative path) - no exploit path was found.

## Adversarial verification (Phase 3)
- Pinned end to end: `git-sha` → error naming `verify_against`; `cache` → the symbol as before.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `6026314bfbd9913a25c882971bcb7ea260a7895cb3f06fb37f777c35db77391d`. TDD: `tests/test_tail_batch3_reaudit.py` (6 tests across the four units of this batch) - all 6 RED on the old bytes (each for its own reason, verified by the per-test failure), GREEN after; the audit probe passes after where one existed.
