# Colibri Review - bug (DELTA) - PatternSkin/presets_data.py

- **Source path:** `PatternSkin/presets_data.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 12
- **sha256 reviewed:** `eda3c675c446f51545a9a557719c3fed7fa981d38cc7f71284bd9bd407642f11` (sha8 `eda3c675`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `d1fd2e6a` (2026-07-24 round 2)
- **Delta reviewed:** 2 commits / 14 diff lines: c19bd131 + 27d74bf3 (Reship #30b/#30c: the two `pattern_file` pins removed, type resolution only) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta - a data-only change; `_find_library_type` resolves both presets by type through the flat library.

## Bugs & vulnerabilities
None confirmed at the delta.

## Adversarial verification pass / notes
- PSK-PRESET-REPIN deferral stands (pins are deliberately absent until picks are made from the current set).

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/presets_data.py

- **Source path:** `PatternSkin/presets_data.py`
- **Reviewer:** claude-fable-5-1 (fork of the lead session), Colibri G37 protocol, campaign item 1 (product cores), rank 12
- **sha256 reviewed:** `eda3c675c446f51545a9a557719c3fed7fa981d38cc7f71284bd9bd407642f11` (sha8 `eda3c675`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the prior records - `d1fd2e6a` 07-24 and today's delta - predate the gate or took it as baseline; no delta)
- **Context pack:** every line read (101, pure literals); the consumers in `__init__.py`: `_preset_cfg_for` 1197-1201, `_preset_is_modified` 1203-1225, `_preset_items` 1298-1308, the property definitions the values land in (`obj_type` 1700, `finish` 1704, `mode` 1707-1716, `tile_mm` 1726, `depth_mm` 1744, `relief` 1747, `contrast` 1966, `resolution` 1968, `depth_falloff` 1895-1900, `autofit_tiles_hint` 1830, `finish_uses_pattern` 1829), `_load_preset` 4704-4771 and `_find_library_type` 787-835 (the tokenizer + consecutive-words rule), the save/update user-preset operators 4809-4860 (`_PRESET_KEYS` consumers); the shipped inventory `PatternSkin/default_library_checksums.json` (294 images, 7 packs, no emblem pack; the installer at 5194-5199 confirms the zip ships none); deferred row PSK-PRESET-REPIN loaded as a claim.

## Verdict
The data is well-formed (every enum value, range and object-type key resolves against its consumer) but THREE shipped presets name a texture type the shipped library cannot satisfy, and the consumer's remedy text sends the user in a loop. Data fix is an art-direction pick (owner), not a blind edit.

## Bugs & vulnerabilities

**[MEDIUM] Three Nexusmill presets ask for `pattern="heraldic crest"`, a type no shipped library file matches - the preset never gets a pattern and the warning's remedy cannot work** - `line 27` (LID "Heraldic crest - deep"), `line 48` (RING "Signet bezel - deep"), `line 79` (DOME "Dome plaque - deep carve")
- What: `_load_preset` resolves `pattern` through `_find_library_type`, which needs the type's words (`["heraldic", "crest"]`) as consecutive whole words of a file stem. The shipped default library is exactly the 294 files of `default_library_checksums.json` (animal_skins, ethnic_cultural, floral_botanical, geometric, industrial_grunge, nature_organic, staples) - no stem carries either word, and the zip ships no emblem pack. The other 16 type words all resolve (verified by the same rule over the manifest).
- Trigger: pick any of the three presets in the dropdown (the pick is the commit).
- Impact: the preset loads with no pattern and `library_status` shows "This preset's 'heraldic crest' texture isn't in your library - use 'Install the included library' in the Pattern section, then pick the preset again" (`__init__.py` 4761-4763) - the user installs the included library, picks again, gets the same message. A shipped recipe that can never do what its name promises, with an instruction that loops.
- Fix: either re-point the three presets at a shipped type (an aesthetic choice: heraldic sits closest to `geometric islamic` / `geometric sacred geo` / `geometric art deco`) or add a heraldic-crest image to the shipped library (money + art direction). Per the repo's own PSK-PRESET-REPIN doctrine ("Damien picks by eye - no silently substituting art direction") this is the OWNER's pick: docket it next to PSK-PRESET-REPIN, and until then the honest mechanical step is the consumer's warning text (a cross-file note, `__init__.py` 4761: it should not promise the included library holds a texture it does not).
- Verification: CONFIRMED by reproducer `probe_ps_presets_data_1.py` (the resolver's tokenizer + rule copied verbatim, run over the manifest basenames): RED on the current data for exactly the three presets; every other preset resolves; stays RED until the data or the library changes (no code fix proposed).

## Missing safeguards (not fixed, no defect traced)
- No harness check ties the preset type words to the shipped inventory - the deferred PSK-PRESET-REPIN row assumed "the type-word fallback keeps every preset resolving", which this probe shows is false for one word. Wiring `probe_ps_presets_data_1.py` into the pure-probe tier closes that gap once the data is fixed.
- Loading a preset leaves keys it does not name (`tile_rotate`, `tile_variation`, `layer_mode`, `invert`, `gamma`, ...) at whatever the previous state was - by design (the 4707 comment), noted because a user may read a preset as a full recipe.

## Adversarial verification pass (refuted claims - one line each)
- "`pattern='geometric'`/`'floral'`/`'scales'`/`'wood_grain'`/`'stripe'` do not resolve" - refuted: each matches a shipped stem under the consecutive-whole-words rule (`geometric_art_deco_*`, `floral_botanical_damask_floral_*`, `staples_scales_*`, `staples_wood_grain_*`, `staples_stripe_*`).
- "`depth_falloff='RADIAL'` / `mode='SWEPT3D'` / `finish='PEARL'` are not valid enum items" - refuted: all present in the scene property definitions.
- "`autofit_tiles=8` exceeds `autofit_tiles_hint`'s range" - refuted: min 1 / max 12.
- "`PS_OBJ_TYPES` passed directly as EnumProperty items is not reference-stable" - refuted: a module-level list, static.
- "integer preset values (`tile_mm=30`) fail on a FloatProperty" - refuted: RNA accepts ints on float properties.
