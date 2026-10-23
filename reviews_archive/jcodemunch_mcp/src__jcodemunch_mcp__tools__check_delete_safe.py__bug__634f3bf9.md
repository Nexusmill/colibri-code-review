# Colibri review — src/jcodemunch_mcp/tools/check_delete_safe.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\check_delete_safe.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `634f3bf9b136785c782b9a09dae2b1dc0666a1ec69b735da4d3670f53ed9df01` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: DELTA against the prior record `…check_delete_safe.py__bug__68d723db.md` (2026-09-05, external grok-4.3 review gated in-session; the file changed since via 86928cf/2a097af/78a76ed); the sub-agent's summary (1 CONFIRMED with a RED probe, 3 refuted); Signal 3 (text refs, 232-278) and its #406 comment - the definition, not the file, is what must be excluded; Signal 6 (SCIP, 314-342) `_scip_files.pop(target_file, None)`; the verdict chain 344-372 (`scip_external_count > 0` → `scip_referenced`, confidence 0.10); `_scip_consume.scip_reference_files` (its own record, same commit); `tests/test_v1_108_120.py` marquee (cross-file edge only) and `tests/test_v1_108_226.py` (the same-file text-ref case).

## Verdict
The tool's whole job - "is this symbol used?" - was answered backwards for a compiler-verified caller in the target's own file: the SCIP channel repeated #406 (drop the FILE when the thing to exclude is the DEFINITION) one channel over from where it was fixed. Fixed.

## Fixed since last review
- The 68d723db record's two refuted external findings (SCIP block can raise out of the tool; `target["id"]` KeyError) remain refuted on these bytes - `scip_reference_files` is still honest-empty on any exception and `id` is still the NOT-NULL primary column. Nothing from that record was open.

## Bugs & vulnerabilities
**[HIGH] `safe_to_delete` for a symbol the compiler proved is called from its own file — CONFIRMED — FIXED** - `line 324`
- What: `_scip_files.pop(target_file, None)` (comment: "self-references are not external uses") discarded every SCIP reference whose caller lives in `target_file`, including a different symbol's call. `scip_reference_files` already excluded `definition` edges, so every popped row was a real reference. Trigger (audit probe, RED on these bytes): `target()` and `caller()` in one module, `caller` reaching `target` through `globals()['tar'+'get']` so the import graph and text channel see nothing; inject the compiler edge caller→target; `check_delete_safe(repo, "target")` → `safe_to_delete`, zero blockers, confidence 0.85.
- Fix: the pop is gone; `scip_reference_files` excludes the target's own recursive edge by identity (same commit). A same-file caller now blocks as `scip_referenced` (`scip_external_ref_count` 1, blocker `scip_reference` with `verification: compiler_verified`); a purely recursive symbol is still `safe_to_delete` (control).

## Refuted (recorded so they are not re-raised)
- `dead_code_conf >= 0.9` branch structurally redundant with the next `elif`: same verdict, no observable difference.
- `_resolve_target` name-collision fallback mixing in unrelated callers: can only make the verdict MORE cautious, never a false safe.
- `runtime_hits` 0 vs None conflated: two distinct signals (`runtime_hits`, `runtime_data_present`) as documented.

## Adversarial verification (Phase 3)
- Asserted end to end through `check_delete_safe` over a real index with an injected `scip_edges` row (fixture shape of `tests/test_v1_108_120.py`); before the edge the verdict is `safe_to_delete`, after it `scip_referenced` with the same-file blocker listed.
- Control: a self-recursive symbol whose only SCIP edge is itself → `scip_external_ref_count` 0, no `_meta.scip`, in both preflights - the identity exclusion does what the file pop was for, without the collateral.
- `tests/test_v1_108_120.py` (cross-file marquee) and `tests/test_v1_108_226.py` unchanged and green.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `e58f2c0f3a7980dad14f194c9bde970d5e4212a1770bc54e2212b0b17d1e707d`. TDD: `tests/test_scip_same_file_caller_reaudit.py` (5 tests, one battery for the shared root cause) - 3 RED on the old bytes (the helper's self-edge exclusion, the delete verdict, the edit verdict), 2 controls green throughout (a same-file edge from a different symbol already reached the helper's output; a purely recursive symbol stays safe in both preflights), GREEN after. Both audit probes (`probe_check_delete_safe_1.py`, `probe_check_edit_safe_1.py`) were RED on these bytes and pass after.
