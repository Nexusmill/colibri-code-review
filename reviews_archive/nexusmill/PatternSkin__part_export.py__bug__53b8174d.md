# Colibri Review - bug (DELTA) - PatternSkin/part_export.py

- **Source path:** `PatternSkin/part_export.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 6
- **sha256 reviewed:** `53b8174d9d2d0c4ce7e07d0c42312b6a7a1c7f6af673b26964b8e84f033c7d9c` (sha8 `53b8174d`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `30d1e2ed` (2026-07-23 hunt round 1)
- **Delta reviewed:** 4 commits / 692 diff lines (the file was re-written line-ending-wise; content delta): 150e64f1 (`_atomic_finalize` for every writer), edfa1188 (PE-1 uniquified STL fan-out), 60bbde28 (GLM-POLISH `_check_geometry(tri_part)` + atomic `open('x')` claim), 69d0c2e2 (GROK-PE2 claimed-placeholder sweep on failure) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json` rows naming the file, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the call sites each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta. Every writer now writes `path + '.pstmp'` and `os.replace`s it in (the temp is removed on any failure); the STL fan-out claims each derived name atomically and sweeps every claimed name - a strict superset of the written ones - when a writer fails; `split_parts` refuses a length-mismatched part map before indexing.

## Bugs & vulnerabilities
None confirmed at the delta.

## Adversarial verification pass / notes
- Missing safeguard (cosmetic): `_unique` treats a permission error the same as `FileExistsError`, so an unwritable directory ends in 'no free filename near ...' after 999 attempts instead of naming the permission problem.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/part_export.py

- **Source path:** `PatternSkin/part_export.py` (junction twin `blender_dev/addons/PatternSkin/part_export.py`, same bytes)
- **sha256 reviewed:** `53b8174d9d2d0c4ce7e07d0c42312b6a7a1c7f6af673b26964b8e84f033c7d9c` (sha8 `53b8174d`, 376 lines)
- **Reviewer:** claude-fable-5-1 (fork of the lead session), colibri G37 FULL bug review
- **Date:** 2026-09-10 - **Mode:** bug, FULL read of the current bytes (owner ruling: the file's pre-gate reviews of 07-20..08-20 are CLAIMS re-verified here, not a baseline)
- **Context pack:** jCodemunch outline (18 functions) + importers (only `filmstrip.py` `PATTERNSKIN_OT_export_parts.execute`, which passes WORLD-space vertices, loop-triangle faces, per-triangle part ids with -1 wrapped to 0, palette colours and a sanitised basename, and forces the .3mf/.stl extension); the sibling whole-object exporter `__init__._write_3mf` (world space, `unit="millimeter"`, no unit scale - the same 1 unit = 1 mm convention, so no cross-exporter scale drift); remediation rows 07-20 (XML injection, write_3mf geometry check), 07-23 (atomic writes, STL fan-out cleanup, docstring), 07-24 (PE-1 uniquify), 08-15 (GLM-POLISH tri_part length check, atomic claim), 08-20 (GROK-PE2 claimed-file sweep); features PS-GROK-R2 / PS-POLISH; `tests/test_part_export.py`; prior records 30d1e2ed / f61070b6 / 53b8174d.

## Verdict
Shippable after two fixes in `write_3mf_bambu`, the DEFAULT export format. Every earlier remediation is present at the bytes (XML attribute escaping, colour validation, geometry + tri_part checks, atomic finalize with temp cleanup, atomic `open('x')` claims, `claimed` superset sweep). The single biggest risk was the one silent-truncation path the GLM-POLISH round missed: the Bambu writer's own 0.01 mm snap.

## Bugs & vulnerabilities

**[MEDIUM] The Bambu/Orca writer silently drops collapsed triangles and only refuses a TOTAL collapse** - `line 253-262` (`degen` filter + `if kept == 0`)
- What: vertices are snapped to 0.01 mm (`np.round(V * 100.0)`) and every triangle that collapses at that precision is skipped; the guard "all triangles degenerate ... check unit scale" fires only when `kept == 0`. `face_count` in `model_settings.config` is written from `kept`, so the config quietly agrees with the shrunken mesh.
- Trigger: a model authored at Blender's default metre scale (a 5 cm object spans 0.05 units) - or any other wrong unit scale that leaves some triangles alive. Reproducer: a 960-triangle sphere of radius 0.025 exports 192 triangles with no error (`probe_ps_part_export_1.py` `PE_bambu_refuses_mass_collapse`, RED).
- Impact: `export_parts` returns the path, the operator reports "Exported 1 file(s)", and the user gets a hollow scrap a few hundredths of a millimetre wide in Bambu Studio - the same class as the GLM-POLISH "truncated mesh exported with a success message" row this file already fixed for tri_part. The other three formats do not snap, so they export the (wrongly scaled but complete) mesh - the default format is the only one that destroys it.
- Fix: refuse when fewer than half the triangles survive (a printable mesh cannot lose half its triangles to a 0.01 mm snap; a legit sliver or two still passes): `pe_fix1` in the summary. Verified GREEN on a scratch copy; `tests/test_part_export.py` still passes against the copy.
- Verification: CONFIRMED (trace + reproducer RED on the current bytes, GREEN on the fixed copy).

**[LOW] The bed-centring transform uses the bbox of EVERY vertex, loose vertices included** - `line 240-241`
- What: `cx, cy` and the `-V[:, 2].min()` rest-on-bed offset are computed over all of `V`; the writer receives the full mesh vertex array from the operator (`me.vertices`), which includes vertices no face references.
- Trigger: one stray vertex below (or beside) the model - a leftover from modelling, common in scanned/kit-bashed meshes; nothing in `_check_geometry` rejects loose vertices. Reproducer: a sphere plus one vertex at z = -400 gets a build transform that lifts the model 375 mm (`PE_bambu_rests_on_bed_with_loose_vertex`, RED).
- Impact: the stored `<item transform>` places the print floating above (or off-centre on) the plate. PLAUSIBLE impact on the slicer side (whether Bambu Studio auto-drops a project 3MF's item is not verified here); the transform itself is wrong by construction.
- Fix: compute the bbox over `V[np.unique(F)]` (`pe_fix2`). Verified GREEN on the scratch copy.
- Verification: CONFIRMED code path; impact PLAUSIBLE (slicer behaviour unverified).

## Missing safeguards
- `_unique._claim` swallows `OSError` as "name taken": an unwritable directory makes the loop try 999 numbered names and then raise "no free filename near ... (999 numbered copies?)", hiding the real permission error. Let a `PermissionError` propagate.
- `write_3mf_bambu` still drops legitimately collapsed slivers silently below the new threshold; the count is not surfaced to the operator (the return contract is a path list). Acceptable - a zero-area triangle does not open the shell.
- `bed_center=(128, 128)` assumes a 256 mm plate; the A1 mini (180 mm) gets an off-centre placement (cosmetic, slicers re-centre on demand).
- Outside this unit, one line: `__init__._write_3mf` (the whole-object 3MF) still opens `zipfile.ZipFile(filepath, "w")` directly - the atomic-finalize discipline this file adopted on 07-23 never reached its sibling.

## Adversarial verification pass (refuted claims)
- "part_export declares millimetres but the operator passes raw Blender units - a unit-scale defect" - REFUTED as a defect: the whole product treats 1 unit = 1 mm (tile_mm/depth_mm are object units; `__init__._write_3mf` exports the same way), so the exporters agree with each other and with the add-on's documented convention; only the Bambu snap turns a wrong scale into a destroyed mesh, which is the MEDIUM above.
- "`_atomic_finalize`'s `.pstmp` name is not uniquified, so two concurrent exports collide" - REFUTED: the temp name derives from the already-claimed unique target, so two exports never share one.
- "`_PAINT_CODES[slot]` is off by one" - REFUTED again (docs/MULTIMATERIAL_EXPORT_RESEARCH.md: index 0 unpainted, slot k -> index k; 17 entries cover slots 1..16).
- "The `rec` structured dtype may be padded to more than 50 bytes" - REFUTED: `np.dtype([...])` without `align=True` is packed (12 + 36 + 2 = 50), and `tests/test_part_export.py` asserts the exact byte layout.
- "`write_stl_binary` checks geometry after the float32 cast, missing float64 overflow" - REFUTED (that ordering is what makes an overflowing coordinate visible as inf).

## Remediation postscript (same session)
The fixes were applied after this review hashed the bytes above; the file is now `71208675d1a6d5602db62c74c1814e68abf831b53bee1c9fc8e75b7810addd96`. Rows PS-PE-BAMBU-COLLAPSE, PS-PE-BAMBU-LOOSE-BBOX in `docs/remediation_manifest.json`, same commit.

