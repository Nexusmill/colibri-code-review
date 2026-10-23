# Colibri review — src/jcodemunch_mcp/tools/get_ranked_context.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_ranked_context.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `0257c3c4ad32c6e9aad77d859a0e51b226f9db5c69678d38d293cb9c6c33cfbc` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 1 refuted); the two savings sites 549-555 and 794-800 (`sum(index.file_sizes.get(file, 0) …)` per scored/packed symbol); `assemble_task_context.py` 734-744, which had already grown the same fallback inline in tranche c5a6f7e (`file_sizes` empty on a fresh `index_folder` view → symbols' `byte_length`); `find_implementations.py` 581 (sums every symbol's `byte_length` - a different baseline, out of scope); `storage.estimate_savings`. No prior `.colibri_reviews` record.

## Verdict
The savings estimate trusted a map that is empty on the very views the tool is most often run against, so it reported "saved nothing" for a scan that read plenty. Fixed with one shared baseline rule, used here at both sites and by assemble_task_context.

## Bugs & vulnerabilities
**[MEDIUM] `tokens_saved` read 0 on a view without `file_sizes` — CONFIRMED — FIXED** - `line 549-552, 794-797`
- Trigger (audit probe, RED on these bytes): 12 widgets in one file, 3 packed → `items_considered 12 > items_included 3`, `tokens_saved 0`.
- Fix: NEW `tools/_utils.file_bytes_for_savings(index, files)` - distinct files, `file_sizes` when present, the file's symbols' `byte_length` when not - at both sites; `assemble_task_context` re-pointed to it (its inline copy removed; its T10 battery unchanged and green). The sub-agent's refuted "once per symbol rather than per file" claim is folded in as a de-duplication the helper does anyway.

## Adversarial verification (Phase 3)
- Pinned end to end (the probe's fixture: `tokens_saved > 0`) and on the helper directly with a fake index (`a.py` sized 1000 by the map, `b.py` sized 300+200 by symbols, duplicates and blanks ignored, an unknown file 0).

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `4dd10bbd68d6367f672d6b81dde8e57fa158b01d0aa5bc72515418549ad73ab8`. TDD: `tests/test_tail_batch3_reaudit.py` (6 tests across the four units of this batch) - all 6 RED on the old bytes (each for its own reason, verified by the per-test failure), GREEN after; the audit probe passes after where one existed.
