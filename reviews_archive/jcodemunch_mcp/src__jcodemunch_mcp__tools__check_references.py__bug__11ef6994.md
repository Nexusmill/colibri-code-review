# Colibri review — src/jcodemunch_mcp/tools/check_references.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\check_references.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `11ef69945642f6d66a0e5aaaf378195a7dced51a83f3ffb587806c3d5da75ee7` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 PLAUSIBLE "disclosed tradeoff", 3 refuted - kept); the `unspanned_files` degrade 70-98 (a same-named symbol without a usable `line` skips its whole file from the content scan - deliberate, documented in the file and pinned by `tests/test_v1_108_226.py::TestUnspannedSymbolsDegradeToTheOldBehaviour`), the result 141-154 (nothing names the skipped files), `_check_batch` 157-193 (strips `_meta`, keeps the body); consumers: `check_delete_safe`/`check_edit_safe` (batch form, read `is_referenced`), `cli/hooks.run_taskcomplete` (reads `is_referenced`), and the agent calling the MCP tool. No prior `.colibri_reviews` record.

## Verdict
The degrade is right and stays; its silence was the defect. `is_referenced: False` could rest on files the scan never opened, with no way for the caller to tell. The skipped files are now named in the result.

## Bugs & vulnerabilities
**[LOW] Files skipped for want of a span were not reported — CONFIRMED — FIXED** - `line 151-152`
- Trigger (RED on these bytes): a symbol with `line=0` whose own file holds a live call → `is_referenced: False`, `content_count: 0`, nothing else.
- Fix: `result["unscanned_files"] = sorted(unspanned_files)` when the content scan ran and skipped any - in the body, so the batch form keeps it per identifier. The scan itself is unchanged (the v1.108.226 pin stays green).
- Follow-up, not done here: `check_delete_safe`/`check_edit_safe` read `is_referenced` only; treating a non-empty `unscanned_files` as unestablished (the T30 deletion_safety pattern) is a consumer-side change for its own pass.

## Refuted (kept from the sub-agent, re-traced)
- Comment/string hits inflate `is_referenced` (documented plain-text behaviour; only adds caution); `setdefault` overwrites (it appends to a list, 98); the `max_content_results` break can make `is_referenced` falsely False (it fires only after `content_count >= 1`).

## Adversarial verification (Phase 3)
- Pinned: single and batch forms name `src/utils.py`; a spanned symbol scans its file (`content_count == 1`, the call outside the span) and carries no key; `search_content=False` carries neither key. 137 green in the check_references/delete_safe/edit_safe/deletion_safety/rename_safe/taskcomplete sweep.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `6b39147de57a97e0da2a3d907952939638e8a30b5f0bb5a7da19c01170d2ba9e`. TDD: `tests/test_check_references_reaudit.py` - 2 RED on the old bytes + 2 controls green throughout, GREEN after.
