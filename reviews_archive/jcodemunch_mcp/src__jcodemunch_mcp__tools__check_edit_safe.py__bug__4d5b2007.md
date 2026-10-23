# Colibri review — src/jcodemunch_mcp/tools/check_edit_safe.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\check_edit_safe.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `4d5b2007988b65563b7678afcea02ed0dcce1dc1d1a976833572016c1836fb57` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted); Signal 6 (SCIP, 213-236) `_scip_files.pop(target_file, None)`; the verdict chain 238-249 (`signature_impact = external_import_count + cross_repo_count + scip_external_count > 0`); the shared helpers imported from `check_delete_safe.py` (`_is_test_file`, `_resolve_target`, `_runtime_hits`, `_runtime_data_present` - covered by that file's record); `_scip_consume.scip_reference_files` (its own record, same commit); `tests/test_v1_108_120.py` marquee. No prior `.colibri_reviews` record.

## Verdict
Same defect as `check_delete_safe.py`, same root cause: a compiler-verified caller in the target's own file was popped by file, and the edit preflight answered `safe_to_edit` for a symbol whose contract another symbol provably depends on. Fixed.

## Bugs & vulnerabilities
**[HIGH] `safe_to_edit` for a symbol with a compiler-verified same-file caller — CONFIRMED — FIXED** - `line 222`
- What: `_scip_files.pop(target_file, None)` discarded any SCIP reference from the target's own file, so `scip_external_count` stayed 0, `signature_impact` stayed False and the verdict fell through to `safe_to_edit` at confidence 0.90 ("no external callers"). Trigger (audit probe, RED on these bytes): the two-function module with a dynamic same-file call plus the injected compiler edge.
- Fix: the pop is gone; self-recursion is excluded by identity in `scip_reference_files`. A same-file caller now yields `signature_impact` with the `scip_reference` blocker ("compiler-verified caller depends on the current contract"); a purely recursive symbol stays `safe_to_edit` (control).

## Refuted (recorded so they are not re-raised)
- `confidence` dict literal KeyError on an unlisted verdict: the verdict comes from an exhaustive if/elif/else over exactly the five keys.
- `is_referenced` omits `scip_external_count`: `signature_impact` (which includes it) is checked first in the chain, so a SCIP-only reference never falls through to `untested`/`safe_to_edit`.

## Adversarial verification (Phase 3)
- Asserted end to end through `check_edit_safe` over a real index with the injected edge: `safe_to_edit` before, `signature_impact` with `scip_external_ref_count` 1 after.
- Control: the self-recursive symbol → `scip_external_ref_count` 0, no `_meta.scip`.
- `tests/test_v1_108_120.py::test_check_edit_safe_flips_safe_to_signature_impact` (cross-file) unchanged and green.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `24b7715d529aef2ee152114b0df30de7e62e260802857d3bd72019a01616003f`. TDD: `tests/test_scip_same_file_caller_reaudit.py` (5 tests, one battery for the shared root cause) - 3 RED on the old bytes (the helper's self-edge exclusion, the delete verdict, the edit verdict), 2 controls green throughout (a same-file edge from a different symbol already reached the helper's output; a purely recursive symbol stays safe in both preflights), GREEN after. Both audit probes (`probe_check_delete_safe_1.py`, `probe_check_edit_safe_1.py`) were RED on these bytes and pass after.
