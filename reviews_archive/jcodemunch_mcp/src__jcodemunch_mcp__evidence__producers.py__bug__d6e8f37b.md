# Colibri review — src/jcodemunch_mcp/evidence/producers.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\evidence\producers.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `d6e8f37b87a6c505e54de6342c218467e02b7bf7b2a8a5261e265570259eeaee` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's review of this unit was PARTIAL (no Phase 3, no probes - "re-run this unit before trusting either finding"), so both of its PLAUSIBLE findings were verified here first: `_norm_file` 83-84 (`lstrip("./")`) feeding `_row_subject` 461-489 (`subject["file"]`, part of what a receipt attests); `mint` 620-798, absence branch 735-777 (`refusal = absence_refusal(record) if record else None` -> `proves_absence: refusal is None`, `absence_record=record`); the consumer `handoff._validate_evidence` 403-437 (a receipt whose frozen `absence_record` is None is refused at finalization - "the scan behind this receipt is no longer on record"); the `search_symbols` producer 215-269 (`symbol_lookup_absence`, rows_key `results`); `tests/test_v1_108_192.py` (mirrors `build_envelope` and pins the producer via a source-string check) + ten other evidence/receipt test files (315). No prior `.colibri_reviews` record.

## Verdict
Two advisory-but-attested fields could lie: a receipt's subject file for a dotdir path, and `proves_absence` for a scan that was never recorded. Both verified by end-to-end mint tests and fixed.

## Bugs & vulnerabilities
**[MEDIUM] `_norm_file` used `str.lstrip("./")` - a receipt for a symbol in `.github/ci.py` bound the subject file `github/ci.py` — CONFIRMED (was PLAUSIBLE) — FIXED** - `line 83-84, 474`
- What: the subject is what the receipt attests; a validator or reader comparing it to the served id sees a file that does not exist. Same class as `handoff._norm_file` (fixed in 729121a) and `token_tracker.note_edited_files`.
- Fix: a literal `./` prefix strip (repeated), backslashes normalised; pinned through a real `mint()` over an indexed `.github/ci.py` symbol.

**[MEDIUM-HIGH] `mint()`'s absence branch claimed `proves_absence: True` when no scan was on record — CONFIRMED (was PLAUSIBLE) — FIXED** - `line 745-777`
- What: `refusal` was computed only when `absence_record(ref)` returned a record; with none, `refusal` stayed None, the receipt said `proves_absence: True` with no limitation, and froze `absence_record=None` - the exact state finalization refuses. The enforcement path was right; the advisory flag in the receipt (what a reader sees between mint and finalize) was wrong.
- Fix: no record -> `refusal = "no scan is on record for this query, so absence is not proven"`, which flows into `proves_absence: False` and the limitation list exactly like a real refusal; a citable scan still proves absence (control).

## Adversarial verification (Phase 3)
- Both defects are asserted through `producers.mint()` end to end - a real index built with `index_folder`, the registered `search_symbols` producer, a retrieval-shaped verdict - and the minted envelope read back with `receipts.lookup`, not through `build_envelope` in isolation.
- The control (`note_absence` recorded a citable scan first -> `proves_absence` True, frozen record present) guards the fix from over-refusing.
- Eleven evidence/receipt test files (315) unchanged: 319 passed with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `fef843e0d090962694f75eaf56ca793f527c62770039bbb4c30ba32db871f6d0`. TDD: `tests/test_evidence_producers_reaudit.py` (4 tests) - 3 RED on the old bytes, 1 control green throughout, GREEN after. (No audit probe existed for this unit; the battery is the reproducer.)
