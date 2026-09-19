# Colibri Review - bug (FULL re-audit) - PatternSkin/ai_parts.py

- **Source path:** `PatternSkin/ai_parts.py` (junction twin `blender_dev/addons/PatternSkin/ai_parts.py`, same bytes)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 2
- **sha256 reviewed:** `c38245dc01d0d35c28b42ebdb6dd346ee55d012e25f144a2f1bde73ef781abcf` (sha8 `c38245dc`, the post-PS-MIRROR-STALE-CHECKPOINT bytes, 2308 lines)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's prior audits - 07-24 r2, 08-14 GROK-AI, 08-20 AIP2, 08-22 AIP6, 08-26 GLM-R2 - predate the adversarial gate and are untrusted; no delta against them)
- **Context pack:** jCodemunch `get_file_outline` (105 symbols) + `find_importers` (only the r3 probe imports it by name - the product callers use `from . import ai_parts as _ap`); every `_ap.*` call site in `__init__.py` (multiview modal 7120-7360, text select 7392-7510, named scan 7549-7762, native-3D 7810-7894, restore 8055, regranulate 8113/8178/8475) and `filmstrip.py` (dress plan 167-311, thumbs 609-624) read; the 30 remediation rows, 8 deferred rows and 15 feature-registry rows naming the file loaded as CLAIMS; the six prior review records listed. Every line read end to end. Probe run headless in Blender 5.1.2 (`--factory-startup`, no network, no spend).

## Verdict
Shippable after ONE fix. The money-safety ladder (`_replicate_create`, `_poll_prediction`, the per-output failure accounting in `sam3_mask`/`_sam2_masks`/`grounded_sam_mask`), the credential fencing (`_urlopen` no-redirect, `_check_poll_url`, `_check_fetch_url`), the lineage/signature cache pairing with the always-refreshed mirror, the atomic writes and the bpy-free worker-thread decoders all hold at the bytes and at every call site. The one CONFIRMED defect is a resume gap in the very checkpoint that exists to protect paid views: a checkpoint recorded after the LAST paid view is refused as "already complete" and the whole scan re-bills.

## Bugs & vulnerabilities

**[MEDIUM] A fully PAID checkpoint (done == n_views) is refused by both resume readers, so a scan that dies in finalize re-bills every view** - `line 1122` (`partial_scan_info`) and `line 1151` (`load_scan_partial`)
- What: both readers test `0 < done < n_views` and return None at `done == n_views` ("already complete: fresh path"). But the checkpoint only exists while `save_scan` has NOT landed - `clear_scan_partial` runs inside `save_scan` (line 1052) - so a checkpoint at `n_views` means exactly "every view was paid and the finalize/save never happened". The multiview modal checkpoints after EVERY successful view including the last (`__init__.py` 7283/7298 with `done = self._i` after the increment), then finalizes on a worker thread (7311-7318); a `finalize_job` failure (7323-7328 CANCELs) or Blender dying during the dense-mesh finalize (the G-HANG-1 case) leaves `done == n_views` on disk.
- Trigger: any multiview scan whose last view checkpoints and whose finalize/save does not complete; then the user re-runs the scan.
- Impact: the pre-flight confirm quotes the FULL price (7126-7138 - `partial_scan_info` returned None) and the run re-bills all views: 14 views = $0.21, deep = $0.42, on the user's own key, for work already bought. The checkpoint file stays on disk, silently useless, until a later `save_scan` clears it.
- Fix (ai_parts, proven GREEN on a scratch copy): accept `0 < done <= n_views` in both readers (done > n_views stays "fresh" - the probe checks it). This MUST ship with the caller change in `__init__.py` or the resumed job renders view `n_views` and IndexErrors on `job["cams"]`: at 7203 set `self._phase = "finalize" if self._i >= self._job["n_views"] else "render"`; at 7137-7138 branch the confirm text for `done >= nv` ("Every view is already paid - finishes the scan for free."); at 7206-7208 the status text likewise. `estimate_cost("scan", nv - done)` already yields 0.0 for the complete case.
- Verification: CONFIRMED - traced end to end and reproduced RED in `probe_ps_ai_parts_1.py` (`CKPT_complete_resumes_into_finalize` FAIL against the repo bytes; the partial/empty/overrun controls PASS), GREEN 4/4 against the fixed scratch copy, RED again against the repo.

**[LOW, PLAUSIBLE] `sam3_mask`'s inflate budget truncates a big answer silently and the partial mask is CACHED** - `line 1926-1932`
- What: when the cumulative `file_size` of the zip's PNGs passes 64 MB the loop `break`s with the PNGs read so far; those decode (`decoded > 0`), so the GROK-AI #4 raise does not fire and the union of a PARTIAL instance set is returned, then persisted by `save_text_select` / used by the named scan as the answer.
- Trigger: a SAM-3 response whose instance masks total more than 64 MB decompressed (roughly 50+ instances at 640 px for one prompt in one view).
- Impact: an incomplete selection that can never be retried without clearing the cache.
- Fix: treat a budget trip as an unusable OUTPUT, not a partial answer: `pngs = []; failures.append("zip over inflate budget"); continue` in place of the `break` - the existing "none usable" raise then keeps it out of the cache.
- Verification: PLAUSIBLE - unverified because it needs a real SAM-3 answer over the budget; the code path is traced, the frequency is not.

## Missing safeguards (not fixed)
- Native-3D scan has no deadline: `p3sam_start` accepts `timeout_sec=1200` and never uses it (dead parameter, the docstring implies a bound that does not exist); `p3sam_poll` returns the same prediction forever when `urls.get` is absent; the modal (`__init__.py` 7835-7860) shows the elapsed seconds and only Esc ends it. A stuck "starting" prediction is an unbounded modal.
- The named scan (up to 3 caption + 48 SAM-3 calls, ~$0.07) has no partial checkpoint - a crash at view 5/6 loses all of it. Deferred-class (small spend), the multiview scan's checkpoint machinery is reusable.
- Missed-vote bookkeeping: `__init__.py` 7253 says a missed view "may be retried on resume", which holds only until the NEXT successful view checkpoints `done` past it (7283); after that the view stays -1 forever. A lost vote, not money.
- `_geo_digest` (line 988) hashes coordinate sums and absolute sums: a compensating multi-vertex edit inside one same-sign region (+d on one vertex, -d on another) leaves both sums unchanged and a checkpoint resumes against edited geometry. The docstring's "any single-vertex move" claim is true; `sha1(V.tobytes())` would close the class at ~40 ms per million vertices.
- Unbounded `r.read()` on delivery-host downloads (`_load_mask` 520, the bare-PNG branch of `sam3_mask` 1907/1938, `p3sam_download` 2162): host-fenced to replicate.delivery/replicate.com, but no size cap - a memory guard is missing.
- `_spector_dir` (line 917) reports Spector's home when only a `spector` module is importable, so `save_scan`/`save_parts` create `~/.spector/inbox` on a machine without Spector installed (cosmetic).
- `assign_view` / `_segment_geometry` size the bincount at `nf * K` (K = SAM mask count, up to ~1000 at `points_per_side=32`): ~330 MB transient at 40k proxy faces. Pre-existing, transient, noted only.
- Cross-file, for the `__init__.py` unit: `_sem_price` (7554) and the native-scan button (5681) carry price LITERALS while the PS-COST-PREFLIGHT registry row claims `PRICE_TABLE`/`estimate_cost` is the single price source - the values agree today (0.00125 = `PRICE_TABLE["sam3"]`) but nothing enforces it; `_drop` at 7736 is always empty because `parse_nouns` (1564) already drops surface words - dead code, harmless.

## Adversarial verification pass (refuted claims - deleted from the findings)
1. `semantic_assign`'s once-per-view `count_covis` is lost when the first live noun's call fails - refuted: the named-scan modal tracks it with `_covis_done` (`__init__.py` 7674, 7727-7729), not by noun index.
2. `p3sam_export_glb` runs in Edit Mode and exports stale mesh data - refuted: the native-3D operator forces OBJECT mode (7812-7813) before calling it.
3. `np.load` NpzFile handles stay open on Windows and block the later `os.replace`/`os.remove` of the same path (`load_parts`, `load_scan_path`, `partial_scan_info`) - refuted: every `z[...]` copies the array, `z` is released at function return under refcounting, and the `except` paths clear the traceback.
4. The `sam3_mask` zip budget is bypassable by a lying `file_size` header - refuted: CPython's `ZipExtFile` caps reads at the declared `file_size`, so the header is the ceiling; only the silent-truncation LOW above survives.
5. `_replicate_create`'s except order lets a pre-send `URLError` fall into the OSError "billed" clause - refuted: `HTTPError` then `URLError` are caught before `OSError` (305/322/333), the framing is deliberate for post-send drops.
6. The text-select panel price (`estimate_cost("text", 8)`) disagrees with the views actually run - refuted: `self._nv = 8` (7421) and the filmstrip dress plan uses 8 (194, 273).
7. `load_scan_partial` hard-codes `use_proxy=True` and corrupts the label transfer for a scan that ran WITHOUT a proxy - refuted: `transfer_labels` over identical proxy/full centroid sets is the identity mapping.
8. A 2xx create body that is JSON but not an object escapes `_poll_prediction` as a raw AttributeError with no billing warning - dropped: Replicate's create schema is an object; no evidence such a body occurs.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `684b6716c6c1718f6e8851f924b698c2f64b54c2f4593e4c304279a4127a6f03`. Rows PS-AIP-CKPT-COMPLETE-REBILL, PS-AIP-SAM3-BUDGET-PARTIAL in `docs/remediation_manifest.json`, same commit.

