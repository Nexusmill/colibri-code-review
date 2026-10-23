# Colibri review — src/jcodemunch_mcp/cli/whatsnew.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\cli\whatsnew.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `7901da65cd69afe7997d3517ded86d08293b5138b8fb46717e068230ca91e106` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED); `update_readme` 95-113 (`pattern.sub(replacement, text)` with the changelog block as a replacement STRING); `render_readme_block` 84-92 (the block is built from CHANGELOG titles - contributor-written text); `main` 136-184 (the release script). No prior `.colibri_reviews` record.

## Verdict
The README block went into `re.sub` as a replacement template, so a changelog title with a backslash sequence either raised or landed altered. Fixed with a callable replacement - the block is text, not a template.

## Bugs & vulnerabilities
**[LOW] Changelog text passed to `re.sub` as a replacement string — CONFIRMED — FIXED** - `line 109`
- Trigger (RED on these bytes): a title containing `\d` → `re.error: bad escape \d`; `\n` → broken into two lines; `\1` → a group reference.
- Fix: `pattern.sub(lambda _m: replacement, text)` - a callable's return value is used verbatim.

## Adversarial verification (Phase 3)
- Pinned: a block with `\d` and `\n` lands byte-for-byte between the markers and `update_readme` returns True.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `8129417cb783dde46dfb9e3cf53aa0a8f7a4ac28e5f6c207906ecfe02cd31375`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
