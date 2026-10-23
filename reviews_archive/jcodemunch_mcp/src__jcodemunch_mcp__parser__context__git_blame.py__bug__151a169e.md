# Colibri review — src/jcodemunch_mcp/parser/context/git_blame.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\parser\context\git_blame.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `151a169eab6645a466cec19a43fee0c337640bb69879b245bd1c24083b37281a` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED); `load` 98-153 (`--format=COMMIT %an|%aI`, `rest.split("|", 1)`); `%aI` is strict ISO-8601 and never contains `|`, `%an` is the author display name (contributor-controlled); `get_file_context` 155-163 (`last_author`/`last_modified` into the index's file context, surfaced by get_file_outline/ranked context). No prior `.colibri_reviews` record.

## Verdict
A `|` in an author's display name shifted the date field. Fixed: the LAST `|` is the name/date boundary, because the date side can never contain one.

## Bugs & vulnerabilities
**[LOW] `COMMIT %an|%aI` split at the FIRST `|` — CONFIRMED — FIXED** - `line 144`
- Trigger (RED on these bytes): author `John | Doe` → `last_author: John`, `last_modified: " Doe|2026-"`.
- Fix: `rest.rsplit("|", 1)`.

## Adversarial verification (Phase 3)
- Pinned with a stubbed `git log`: `last_author == "John | Doe"`, `last_modified == "2026-01-01"`. A name without `|` splits identically to before.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `788cd172a42ea32773a53e72986be1f327c310b5efe9ee2fa948fadd77dddee1`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
