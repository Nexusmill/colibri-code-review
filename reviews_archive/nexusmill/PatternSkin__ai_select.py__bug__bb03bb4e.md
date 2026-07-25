# colibri-review — PatternSkin/ai_select.py — bug (hunt round 1, effort=mid)

- **Source:** PatternSkin/ai_select.py · **Scanner:** general-purpose subagent @ claude-sonnet (mid
  effort) · **Verification:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** bb03bb4ef0e817b33f9a4be4c52ad5a62d54018308548ffa1f35af7cee794999
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (mid pass)
- **Context pack:** prior review `PatternSkin__ai_select.py__bug__d1808692.md` (K3) + remediation rows
  (df7b785, glm20-2) — the prior `look_at_basis` degenerate fallback, `cam==center` zero-basis,
  unvalidated `dual_edges`, and adjacency-bounds findings all verified fixed (scanner fuzzed
  `look_at_basis` over 2M adversarial trials → 0 bad results). Callers traced: `ai_parts.py`
  (24 sites) + `__init__.py` state machine.

## Verdict
Clean this round. Every prior HIGH/MEDIUM is fixed in current bytes, and the only new finding is
dead code (not a functional bug). Several candidate bugs were traced and refuted. No change made;
stays active for a higher-effort round.

## Findings
No functional defects confirmed.

## Quality / bookkeeping notes (not bugs)
- **Dead code `_otsu` (`ai_select.py:204`)** — zero references repo-wide (`find_references`=0). Not a
  functional defect (unreachable, no runtime cost); a staleness signal (the thin/thick split now
  goes through `_sdf_levels`, not Otsu). A quality-pass cleanup, not a bug-mode fix — recorded, not
  fixed this round.
- **G35 bookkeeping gap** — the prior `refine_parts_by_geometry` re-pack fix (edgeless path now
  re-packs via `np.unique`, verified present at :245-250) appears to have landed without a
  remediation-manifest row. Noted for the record; not fabricating a commit hash to back-fill.
- **Still-open LOW (already on record):** an all-`-1` connected region with no visible neighbour
  stays `-1` after the `while changed` flood (`assign_unseen_to_parts` and its two reuse sites).
  Carried from the prior review; no new trigger.

## Refuted during verification (recorded in `_refuted_ledger.json`)
- *"`_merge_fragments` merge-order strands a 3-component chain"* — the scanner built a verbatim
  6-face probe: the split does occur after iteration 0 but **self-heals** by iteration 1 (the
  original dual edge (3,4) now spans the two survivors and merges them), well within `max_iter=64`,
  because per-edge `co`/`agree` are cached against raw edge indices, not group aggregates. REFUTED.
- *"`coarsen_labels(target<=0)` sends every face to -1"* — unreachable: the only caller chain passes
  `min(len(uniq),12)` (≥1, `RuntimeError` earlier if zero) or `s.ai_parts_gran`, a Blender
  `IntProperty(min=2,max=60)` also clamped `max(2,min(60,…))` at both write sites. Latent gap, no
  live trigger.
- *"`project_points` `aspect=width/height` divides by zero"* — `res`/`width`/`height` always come
  from positive UI-bounded render resolutions; fails loud, not reachable with 0.
- *"finalize's `ValueError` from `lift_masks_to_parts` crashes the paid modal / loses money"* — the
  operator `modal()` body is wrapped in an outer `try/except` that reports + cancels cleanly, and
  per-view `save_scan_partial` checkpointing already ran. Mitigated at the operator level.
- *(cross-file, noted for `__init__` round 2)* the scanner's "resume indexes past the views array if
  `resume_done == n_views`" hypothesis is **already prevented** by `load_scan_partial`'s
  `if not (0 < done < n_views): return None` guard (verified in unit 2) — `resume_done` is strictly
  `< n_views`, so the fresh-`invoke` `self._i = self._resume_done` can never start at the end.
