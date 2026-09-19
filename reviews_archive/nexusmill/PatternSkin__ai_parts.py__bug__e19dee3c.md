# Colibri Review - bug (DELTA) - PatternSkin/ai_parts.py

- **Source path:** `PatternSkin/ai_parts.py` (2302 lines; the PAID AI part-scan path - Replicate SAM-2 / SAM-3 / grounding-dino / grounded_sam / P3-SAM / VLM captions)
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 2
- **sha256 reviewed:** `e19dee3c5c1e53caae0808e56138a5759a82a7a316cef2363bfe6d9754dc1192` (sha8 `e19dee3c`) - the PRE-fix bytes at HEAD 63ff21e9
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against the last review (`80bcabbf`, the 2026-08-22 grok round-6 gate, 7 findings all CONFIRMED) plus the 2026-08-27 debug record (`be1ea09f`, PSK-SAM3-EMPTYZIP)
- **Delta reviewed:** 5 commits since the review's bytes (`69d0c2e2..63ff21e9`): ae8fc346 (GROK-AIP6 remediation), f6d70d3e (PS-TRANSPORT-1: one `_replicate_create` for all six paid create loops), 83d109f8 (GLM-R2 `HTTPException` billed framing), d82f8de0 (PSK-SAM3-EMPTYZIP), 98900564 (PSK-SCAN-PARTQ: `caption_subject`, `_absorb_fragments`, the "everything else" catch-all) - 853 diff lines read end to end.
- **Context pack:** jCodemunch `get_file_outline` (105 symbols), `get_symbol_source` on `_mirror_to_signature`, `save_scan_partial`, `mesh_signature`, `scan_lineage`, `_paid_cache_candidates`, `_paid_cache_find`, `clear_scan_partial`, `_partial_path`, `partial_scan_info`, `load_scan`, `prune_cache`, `_poll_prediction`, and the callers in `__init__.py` (`PATTERNSKIN_OT_ai_parts_native.invoke/modal`); `search_text` over the harness for the file's batteries (`grok_r6_fixes_bpy.py`, `sam3_emptyzip_fixes.py`, `grok_ai_billing_bpy.py`). `docs/remediation_manifest.json` rows from 2026-08-13 on (psk-ultra-tranche, ultra-gate-2, grok-tranche2, grok-ai-billing, GROK-AIP2, GROK-FILM5, GROK-AIP6, GLM-R2-*, PSK-SAM3-EMPTYZIP); `docs/deferred_manifest.json` (PSK-SCAN-PARTQ now resolved). `_hunt_plan.json` rank 2 (rounds 1-2) and `_refuted_ledger.json` loaded.

## Fixed since last review (GROK-AIP6, all seven verified present at the bytes)
- #1 path traversal via `ps_scan_lineage` -> `_is_canonical_lineage` gate in `scan_lineage` (poison is treated as absent, re-minted on create).
- #2 lineage-only artefacts orphaned on an unsaved lineage -> `_mirror_to_signature` at all four writers (`save_scan`, `save_scan_partial`, `save_text_select`, `save_parts`). Present, but INCOMPLETE for the checkpoint stream - see the finding below.
- #3 non-JSON 2xx create body escaped raw -> `_decode_created` (JSONDecodeError is a ValueError) raises the billed framing; one call site after PS-TRANSPORT-1.
- #4 `p3sam_poll` null body / raw transport error -> null keeps the previous pred, errors wrap with the prediction id; the native modal additionally tolerates five consecutive poll failures.
- #5 GLB import before the try -> import and bindings inside the try, the finally recomputes the import's datablocks from the pre-import snapshots.
- #6 temp PNG orphans -> `_save_temp_png` unlinks on save failure (three renderers).
- #7 temp GLB orphan on export failure -> `except` unlinks before re-raising.
- The debug record's fix (SAM-3 empty ZIP = a real empty answer; captured per-output failure reasons) is present; the modal's missed-vote streak is in `__init__.py` (reviewed in that unit).

## Verdict
Shippable after the one fix below (applied this session, RED-first). PS-TRANSPORT-1 is the right shape: six copy-pasted create loops became one ladder whose every rung is a recorded decision, and the GLM-R2 `HTTPException` clause now covers all six callers at once. The one gap left is inside the AIP6 #2 remedy itself: the signature mirror never refreshes, so for the checkpoint stream it preserves only the first paid view.

## Bugs & vulnerabilities

**[MEDIUM] The signature mirror is written only when absent, so the checkpoint mirror freezes at view 1** - `_mirror_to_signature` `238-239`, called from `save_scan_partial` `1098`
- What: `save_scan_partial` rewrites `{lineage}_partial.npz` after every paid view (done = 1, 2, ... n). `_mirror_to_signature` copies it to `{signature}_partial.npz` only `if not os.path.isfile(dst)` - the first checkpoint creates the mirror and every later one leaves it at done=1.
- Trigger: a scan that checkpoints k views, then Blender dies (or is closed) BEFORE the .blend is saved - the object's `ps_scan_lineage` is lost with it. On reopen `partial_scan_info` / `load_scan_partial` find only the signature-keyed mirror (`_paid_cache_candidates`: lineage None, then signature), which says done=1 (geometry digest and transform still match, so it is accepted).
- Impact: the pre-flight dialog offers "Resumes at view 2/n" and the run re-bills views 2..k - nearly the whole scan - in exactly the crash-before-save case the mirror was introduced to protect (its own docstring). Full-scan and text-select mirrors go stale the same way on a re-run under the same lineage (an older but valid answer is served after a lineage loss - not a re-bill, so LOW there).
- Fix (applied): the mirror is always refreshed, atomically (`copyfile` to `dst + ".tmp.npz"`, then `os.replace`), still best-effort and never raising. Battery `tests/harness/probes/sweep_ai_parts_r3_bpy.py` (hand-built package context, no bpy scene needed): rewrite-then-mirror must read the new bytes (watched RED: the mirror still held the first bytes), no `.tmp` leftovers, a failing copy never raises and never touches the primary; GREEN after; the round-6 battery `grok_r6_fixes_bpy.py` (which owns the original mirror checks) still rc 0.
- Verification: CONFIRMED by trace through `save_scan_partial` -> `_mirror_to_signature` -> `_paid_cache_candidates` -> `partial_scan_info`, and by the headless reproducer.

## Missing safeguards
- Two objects with identical geometry (same `mesh_signature`) and different lineages now overwrite each other's signature mirror; readers prefer the lineage file, so this only matters after a lineage loss, where the fresher equivalent scan is served. Noted, not a defect.
- `prune_cache` is size-only (oldest first) and does not distinguish a mirror from its primary; a pruned mirror simply re-appears at the next write.

## Adversarial verification pass (refuted -> `_refuted_ledger.json`)
- "`p3sam_poll` now raises on any transport error, so one bad poll GET aborts a billed P3-SAM run" - REFUTED: `PATTERNSKIN_OT_ai_parts_native.modal` (`__init__.py:7840-7849`) catches the poll exception and tolerates five consecutive failures before re-raising.
- "A stale signature-keyed partial survives a completed scan and later offers a paid 'resume'" - REFUTED for the completed case: `clear_scan_partial` removes every `_paid_cache_candidates` path (lineage AND signature) once `save_scan` lands.
- "`_replicate_create` re-POSTs on a 422 for callers without `alt_input_on_422`" - REFUTED: the slim retry runs only when an alternate input is supplied and only on attempt 0; otherwise the 422 raises (unbilled, rejected before creation).
- "`sam3_mask` can return an empty mask with zero decodes and zero recorded failures (a silent poisonable empty)" - REFUTED: every non-decoded output path appends a failure or counts a clean empty; the only zero-failure zero-decode outcome is the clean-empty answer, which is a real result.

## Remediation postscript (same session)
The fix was applied after this review hashed the bytes above; the file is now `c38245dc01d0d35c28b42ebdb6dd346ee55d012e25f144a2f1bde73ef781abcf` (9 insertions / 3 deletions). Row PS-MIRROR-STALE-CHECKPOINT in `docs/remediation_manifest.json`, same commit.
