# Colibri review — src/jcodemunch_mcp/cli/skills.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\cli\skills.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `3f2485e4f5488d8f9166bcc421dab46125b15f7ac359e4f81578436adf0c1656` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED); `_has_skill` 48-55 (marker-only: any file carrying `_SKILL_MARKER` counts as installed), `install_claude_skill` 208-232 (returned "already present" before comparing a byte), `_build_skill_content` 58-205 (tier-filtered through `_filter_policy_for_tools` - the body legitimately changes across package versions and tool tiers, which is exactly what goes stale); `uninstall_claude_skill` (marker check, untouched); `tests/test_skills.py` (`test_idempotent_when_already_present` asserts the substring "already present" - kept). No prior `.colibri_reviews` record.

## Verdict
An installed jcodemunch skill was never refreshed, so the tool list a user's agent loads froze at whatever package version first wrote it. Fixed: same bytes → nothing to do; different bytes → ours, refreshed (backup kept).

## Bugs & vulnerabilities
**[LOW] An existing marked SKILL.md short-circuited every later install, however stale — CONFIRMED — FIXED** - `line 221-222`
- Trigger: a SKILL.md written by an older package (or under another tool tier) → every `init`/`install` returns "already present"; the body never catches up with the current tool list.
- Fix: the content is built first; a marked file with identical bytes → "already present and up to date"; different bytes → `would refresh` under dry-run, else `.md.bak` (when `backup`) and rewrite → "refreshed". A foreign (unmarked) file keeps the old path untouched.

## Adversarial verification (Phase 3)
- Pinned end to end: a stale marked file → "refreshed", body equals `_build_skill_content()`, backup holds the stale bytes; a second call → "up to date", no second backup. Control: dry-run and first write behave as before.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `bbf3285d7b4f894a31b801da92e501204aa887c94736563b37a81e1e93c85939`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
