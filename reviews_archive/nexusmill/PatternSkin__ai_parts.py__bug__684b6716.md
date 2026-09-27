# Colibri Review - bug (DELTA pass, perfection R1) - PatternSkin/ai_parts.py

- **Source path:** `PatternSkin/ai_parts.py` (junction twin `blender_dev/addons/PatternSkin/ai_parts.py`)
- **Reviewer:** zcode:glm-5.3 (session model), Colibri G37 protocol, perfection-protocol run R1 (docs/PERFECTION_PROTOCOL.md v3), posture passes A-D
- **sha256 reviewed:** `684b6716c6c1718f6e8851f924b698c2f64b54c2f4593e4c304279a4127a6f03` (sha8 `684b6716`, 2315 lines, the post-7e12b526 bytes; the only delta vs the prior full review c38245dc is the three gated 7e12b526 hunks - re-reviewed under the stale-file DELTA flow)
- **Date:** 2026-09-25 · **Mode:** bug (delta) + failure-paths (B) + introduction-classes-on-delta (C) + domain invariants (D)
- **Context pack:** jCodemunch get_file_outline (117 symbols) + find_importers + lazy-import census (14 `from . import ai_parts` sites in `__init__.py`, 2 in `filmstrip.py`); the 37 remediation-manifest entries naming the file; the prior full review `.colibri_reviews/PatternSkin__ai_parts.py__bug__c38245dc.md` + its deferred list; the 7e12b526 diff (the only unreviewed delta); pyflakes 4.0.0 deterministic pass; battery baseline 30/30 GREEN on the untouched bytes. Full file read end to end at the reviewed sha. Write lease junk/perfection/ai_parts/LEASE.json.

## Verdict
Shippable after one small wave. The money-safety ladder, credential fencing, cache-key doctrine
(readers never mint), atomic-write pairing and the 7e12b526 delta (re-bill guard, zip-budget
cache-poison fix) all hold at the bytes. Three new findings: one MED money-adjacent (prune can
delete paid checkpoints), two LOW hygiene (deterministic pins). Remediated same-session under
Fix-Contracts (junk/perfection/ai_parts/contracts_r1.md), RED->GREEN, battery green, twin synced.

## Bugs & vulnerabilities (new vs the c38245dc record)

**[MEDIUM] prune_cache deletes paid `_partial.npz` checkpoints under budget pressure** - `line 1218` (pre-fix numbering)
- What: the prune loop keeps every `.npz` candidate with no `_partial` exclusion. A cancelled-but-resumable
  scan's checkpoint (and its signature mirror, same suffix) is prunable oldest-first the moment the cache
  exceeds its budget - exactly the artefact class whose purpose is "never re-pay for a paid scan". A later
  text-select or parts save (both call prune_cache post-save) can be the prune that deletes a foreign
  scan's checkpoint.
- Trigger: cache total > budget (default 500 MB) + a checkpoint older than the files being kept + any
  later save (or direct prune) - then the user resumes the scan.
- Impact: the pre-flight quotes the FULL price again for the remaining views (the exact re-bill class
  PS-AIP-CKPT-COMPLETE-REBILL closed).
- Fix: skip-only guard at the loop head (`fn.endswith("_partial.npz") -> continue`) - checkpoints also
  stop counting toward the budget. Contract PER-AIP-R1F1.
- Verification: CONFIRMED at the bytes (no exclusion anywhere in prune_cache; T1 RED on the pre-fix
  bytes removed all four seeded files, GREEN after keeps both partials + prunes the scans; T3 proves the
  cross-artefact sibling through the real save_text_select path).

**[LOW] 18-19 pyflakes dead-import findings** - module header + 7 function scopes (pre-fix lines 13, 19, 355, 1111, 1146, 1269, 1392, 1616, 1837, 1895, 2022, 2082, 2127)
- Vestigial pre-PS-TRANSPORT-1 function-level transport imports (`urllib.error`/`random` and five
  fully-dead import lines) + module-level `sys`/`Vector` + dead `os`x3 + `bmesh`x1. All transport now
  lives in `_replicate_create`/`_poll_prediction`/`_load_mask`, which keep their imports (verified used).
- Verification: CONFIRMED deterministically (pyflakes 19 findings RED -> 0 GREEN; the pin is wired into
  tests/test_perfection_ai_parts.py). Contract PER-AIP-R1F2.

**[LOW] dead accumulators `base` and `allF` in p3sam_labels_from_glb** - pre-fix lines 2194/2223
- `base` incremented, never read; `allF` appended, never concatenated. Deleted. AST probe pins the
  invariant. Contract PER-AIP-R1F3. CONFIRMED.

## Refuted during Phase 3 (deleted, with reasons)
1. `vlm_nouns` returning a dict output would flow into parse_nouns - refuted: the qwen/moondream output
   schema is pinned at the paid probe (list of strings or string); parse_nouns(str(dict)) degrades to
   junk nouns without crashing; no live evidence of a dict output.
2. `_text_votes` normalized-box heuristic misreads sub-2px pixel boxes as normalized - refuted: a box
   whose coordinates are all <=1.5 px is unusable either way (x1<=x0 drops it); the heuristic is the
   documented defensive normalize path.
3. `load_text_select` legacy-migration rename race strands a reader - refuted: the losing thread falls
   back to `path = legacy`, and the consumer's `os.path.isfile(path)` re-check turns the strand into a
   cache miss (one extra bill in a concurrency shape the single-modal UI does not produce).

## Adjudications (deferred LOWs carried from c38245dc - adjudicator: this session's gate round, see gate context)
- p3sam no deadline (timeout_sec dead parameter), named-scan no checkpoint, missed-vote bookkeeping,
  _geo_digest compensating-edit weakness, unbounded delivery reads (x3), _spector_dir cosmetic,
  nf*K bincount transient: all remain deferred with the c38245dc evidence notes; none re-raised as new.
- NEW adjudication this round: `_mirror_to_signature` may leave a `<dst>.tmp.npz` orphan on a mid-copy
  failure - ADJUDICATED LOW (evidence: the orphan ends `.npz` so prune_cache reclaims it; bounded one
  file per failure; the primary save is unaffected - best-effort by recorded design).

## Postscript (same session)
Wave R1 applied (15 hunks: 1 guard + 14 dead-code deletions) -> sha256
`4dd69b09923bc1ce` (full sha in the run record). RED->GREEN evidence: 6 failing checks pre-fix ->
7/7 post-fix (tests/test_perfection_ai_parts.py); full battery 31 files with ONE unrelated flake:
test_hunt_r5_fixes.py segfaults INTERMITTENTLY under system Python (pip-bpy native RNA crash at
__init__.py:7254 + accel probe threads; faulthandler stack captured; ai_parts absent from the stack;
PASSES 4/4 under `blender -b -P` as designed and passed the untouched-bytes baseline on the same
runner). Recorded as a pre-existing test-infra flake, not a wave regression. Twin synced byte-identical.
