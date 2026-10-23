# Colibri review — src/jcodemunch_mcp/storage/selective.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\storage\selective.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `91202292bc6ddbf2d5627913e3848768bc5a0475615068e93688ef91e0a4348c` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted; the review stopped early on a credit limit after the record was written); `_promoted` 167-195 (check `_full is None`, then `_promote()` - the 7-11 minute `load_index` on a large repo - then the bookkeeping), `__slots__` 94-99, `__init__` 101-123 (`object.__setattr__` throughout); the invariant the module documents (`promotions` never exceeds 1); `tests/test_selective_snapshot.py` (33). No prior `.colibri_reviews` record.

## Verdict
The promotion was a check-then-act with no lock: two threads that both saw `_full is None` both paid the full load and both counted it. Fixed with a double-checked lock; the single-thread path is unchanged.

## Bugs & vulnerabilities
**[MEDIUM] `_promoted` raced: concurrent readers promoted twice — CONFIRMED — FIXED** - `line 169-183`
- Trigger (audit probe, RED on these bytes): two threads read `view.symbols` while a slow `promote` is in flight → `promote()` called twice, `promotions == 2`.
- Fix: a `threading.Lock` in `__slots__`/`__init__` (`_promote_lock`); `_promoted` returns fast when `_full` is set, otherwise takes the lock and re-checks before promoting. The bookkeeping (`_promotions`, `_promoted_by`, `_generation_moved`) is unchanged and now runs once.

## Refuted (recorded so they are not re-raised)
- `EXACT_FIELDS` listing a corpus-dependent field; `get_symbol`'s targeted fetch returning a newer-generation row: both re-traced and stand refuted.

## Adversarial verification (Phase 3)
- Pinned with the probe's two-thread harness (`promote` blocks on an event until both threads are inside): one build, `promotions == 1`; control: a single promotion still records `promoted_by` and `generation_moved`, and a second read is free. `tests/test_selective_snapshot.py` unchanged.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `02b4575a2602800603914053ebaddf922da54ae65cb161e83dfb1d251c1bf797`. TDD: `tests/test_tail_batch2_reaudit.py` (7 tests across the four units of this batch) - 4 RED on the old bytes, 3 controls green throughout, GREEN after; the audit probe passes after.
