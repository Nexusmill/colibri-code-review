# Colibri Review - bug (DELTA) - PatternSkin/printfit.py

- **Source path:** `PatternSkin/printfit.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 21
- **sha256 reviewed:** `4362464f4b237792895fb1aa1ff3bf1535147c64d440e1ee359556926fce2f63` (sha8 `4362464f`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `4bde03a8` (2026-08-06 never-scanned sweep)
- **Delta reviewed:** 1 commit / 139 diff lines (a line-ending rewrite; content delta = GLM-POLISH: `slicer_notes` mirrors `_print_reco`'s layer>0 guard instead of printing 'use <= 0.00 mm') - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json`, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the symbols each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta - pure arithmetic and text; the unconfigured-layer branch now names the third-of-relief rule instead of a zero.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/printfit.py

- **Source path:** `PatternSkin/printfit.py` (junction twin identical)
- **sha256 reviewed:** `4362464f4b237792895fb1aa1ff3bf1535147c64d440e1ee359556926fce2f63` (sha8 `4362464f`, 71 lines)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), colibri G37 FULL bug review
- **Date:** 2026-09-10 - **Mode:** bug, FULL read of the current bytes (owner ruling: the file's pre-gate reviews of 07-20..08-20 are CLAIMS re-verified here, not a baseline)
- **Context pack:** jCodemunch outline (3 functions) + importers: `__init__.py` (`print_check`, `slicer_notes` at the 3MF/STL export sidecars 3383/3443 and the guide saver 5942 which writes UTF-8, `_print_reco`) and `filmstrip.py` (`_print_reco`, plus its own `_film_fit` twin at 425-434); remediation rows 07-25 (TEST-PSMATH-1 - `tests/test_patternskin_math.py` imports this module headless) and 08-15 (GLM-POLISH layer>0 guard); feature PS-POLISH; prior records 4bde03a8 / 4362464f.

## Verdict
Clean. Pure arithmetic with the zero guards in place: `print_check` only warns when the layer/nozzle is configured (> 0); `slicer_notes` never prints a `<= 0.00 mm` layer line (the GLM-POLISH guard is present and the unconfigured branch still gives a usable third-of-relief hint, never 0 because of the `max(0.08, ...)` floor); `_print_reco` returns `depth_ok`/`tile_ok` True when the corresponding setting is unconfigured. The em-dashes in the warning strings are fine: the guide writer opens its file with `encoding="utf-8"` and Blender reports are UTF-8.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards / notes
- `filmstrip._film_fit` (lines 425-434) re-implements `_print_reco`'s formulas on the per-part entry instead of calling into this "one source of truth" module - the numbers agree today; the duplication is the risk, not a defect.
- `print_check` compares the unrounded `2 * layer_mm` while `_print_reco` rounds `min_depth` to 2 decimals: at the third decimal (layer 0.1249 mm) the two can disagree by 0.0002 mm - invisible at the 2-decimal UI, noted for completeness.

## Adversarial verification pass (refuted claims)
- "`slicer_notes` can still print a zero layer line when `depth_mm` is 0" - REFUTED: `max(0.08, round(0/3, 2))` = 0.08, so both branches print >= 0.08.
- "The em-dash breaks the exported guide on Windows" - REFUTED: the saver writes UTF-8 explicitly (line 5942); the 3383/3443 sidecars go through the same `note` string into the add-on's own writer.
