# Colibri Review - bug (FULL re-audit) - asset-forge-user/forge/bundle.py

This file is the byte-identical twin (G23) of `asset-forge/forge/bundle.py` at the reviewed sha; the review below is that file's record, reproduced here so the twin carries its own record. Every fix was applied to both files.

---

# Colibri Review - bug (FULL re-audit) - asset-forge/forge/bundle.py

- **Source path:** `asset-forge/forge/bundle.py` (twin `asset-forge-user/forge/bundle.py` byte-identical)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF stale units)
- **sha256 reviewed:** `4220ca3c53877f8e465047d57e1b226b6cd1ab63b59dccd01f2061c380a11735` (sha8 `4220ca3c`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review (pre-gate ruling)
- **Context pack:** FULL read of the current bytes (owner ruling 2026-09-10: the unit's 07-22..08-15 reviews predate the gate and are untrusted); jCodemunch get_file_outline + find_importers; every remediation/deferred row naming the file loaded as CLAIMS and re-checked at the bytes; call sites traced (app.py bundle job + prog callback, library_gen, gen_bundle.py, concurrency.map_bounded/imap_bounded/Stop). Twin asset-forge-user/<same path> byte-identical (sha256 equal) - one review covers both.

## Verdict
Shippable after two fixes (both watched RED on the HEAD bytes, GREEN on a patched scratch copy with grok_t1_billing, grok_r5_fixes, af_transparency_probe, lg_money_resume and af_output_knobs still ALL PASS against that copy). The money rules inside the worker hold: one generation per item, one floor retry at a deterministic alt seed, every billed prediction id kept, the replay path never re-runs the floor, RESERVED_PROPS stripped in the request builder, the all-or-nothing abort receipt names the billed subset. Both defects sit at the EDGES of that receipt contract.

## Bugs & vulnerabilities

**[MEDIUM] A cancel raised from `on_progress` drops the just-completed, BILLED item from the abort receipt** - `line 308-311`
- What: `on_progress` fires AFTER an item was generated, embedded and previewed (i.e. after it was billed and its png written). app.py's only cancel path for a Studio bundle is `prog()` RAISING `_Cancelled` from that callback. The raise is caught by the worker's all-or-nothing handler (`except BaseException` at 324: trip + re-raise), so `imap_bounded` records `(i, spec, None, _Cancelled)` and the item's result dict never reaches `_results` - `INCOMPLETE.json` reports `aborted_after "0/3"`, an empty `billed_prediction_ids` and no `billed_items` while one paid png sits in the directory.
- Trigger: press Cancel on a running bundle (every cancel lands in this callback; with workers=1 the very first cancel reproduces it).
- Impact: G19 - the receipt the customer reconciles their spend against under-reports by exactly the last paid image; the app then marks the job `cancelled` with that receipt.
- Fix (snippets 5-8): build the result dict first; call the callback inside the progress lock in a try; on a raise keep the record, trip the stop with kind "cancelled", remember the exception and re-raise it right after `map_bounded` returns (inside the INCOMPLETE try, so the receipt lists every billed item, and app.py still sees `_Cancelled`).
- Verification: CONFIRMED - probe `BD_cancel_receipt_names_every_billed_item` RED (`aborted_after 0/3`, no ids) → GREEN (`1/3`, `["pred-100"]`, seq 0). Cross-file: app.py's comment at 1088 ("this callback fires BEFORE image i generates, so i-1 is the completed count") is false against these bytes - the callback fires after completion with the completed count, so `job["done"] = i - 1` under-reports by one (app.py's unit; cosmetic).

**[LOW] Setup that runs AFTER `out.mkdir` and BEFORE the guarded loop can still leave an orphaned, unmarked output directory** - `line 90` (mkdir) vs 147-159 (provider, catalogue) and 152 (`theme.lower()`)
- What: the upfront guards (lines 53-89, "validate BEFORE creating out_dir") check buyer/recipe shape/seeds but not the recipe's `theme`/`model` TYPES, and `ReplicateProvider(model)` (missing token → RuntimeError; slug regex; schema fetch) plus `_lib.categories()` run after the mkdir and before the `try` that writes INCOMPLETE.
- Trigger: a hand-edited/shared recipe with `"theme": 5` or `"model": ["x"]`, or any provider-construction failure (no token via `gen_bundle.py`, which has no wrapper).
- Impact: the exact GROK-BD orphan-dir class the guards were written to close: an empty output directory with no marker.
- Fix (snippets 1-4): type-check `theme` (non-empty str) and `model` (str) with the other upfront guards; create `out` and `previews/` only after the provider and the reference catalogue exist.
- Verification: CONFIRMED - three probe checks RED (unmarked dir left for theme=5; no raise at all for model=["x"] with a permissive provider; unmarked dir left when the provider raises) → GREEN.

## Missing safeguards (not fixed)
- A replay item whose `delivered_seed` equals its `seed` (the original was not floor-retried) runs the quality floor again; if the floor's thresholds moved since the original run (MIN_SATURATION landed 2026-08-10) the same image can be rejected and a second seed billed - the recipe records `quality_floor` as a bool, not the thresholds it ran with.
- A recipe with `"items": []` produces an empty signed bundle (count 0) with no spend and no warning.
- The abort receipt's `error` text is the only place the TRIPPING item's own prediction id can appear; the id is present only when the BilledFailure message carries it (see the replicate_flux review, fixed there).

## Adversarial verification pass (refuted claims)
- "`_af_raw_{set_id}_{i}.png` in the shared temp dir is a predictable name (symlink hazard)" - refuted: set_id hashes `secrets.token_hex(6)`, unpredictable per run.
- "the progress lock serialises every worker's post-processing" - refuted: only the callback and the counter run under it.
- "`final.rename(_fdst)` races on Windows" - refuted: names are unique per item; the collision loop checks existence first.
- "a cancel abandons other workers' PAID in-flight items" - refuted: started workers finish and return their dicts (imap_bounded), only never-started items are skipped.
- "recipe `base_seed` as a string breaks `int(base_seed) + i`" - refuted: that expression is on the non-recipe path; the recipe path int-checks `_eff_seed` upfront and casts at the manifest.

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `8feab1eaa78f90b4a96e1d8104aae37bb5e451865455a7a00e0e9804376a3563`. Rows  in `docs/remediation_manifest.json`, same commit.

