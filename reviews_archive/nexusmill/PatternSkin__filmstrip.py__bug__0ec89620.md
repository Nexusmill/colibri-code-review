# Colibri Review - bug (FULL pass, perfection R1) - PatternSkin/filmstrip.py

- **Source path:** `PatternSkin/filmstrip.py` (twin `blender_dev/addons/PatternSkin/filmstrip.py` - symlink, same physical file, sha identical)
- **Reviewer:** glm-5.3 (ZCode in-session), Colibri G37 + perfection protocol L2 postures A-D
- **sha256 reviewed:** `0ec896205742a9e5f872a903bee644d3b34f9117641799aaf94122b4799f98df` (sha8 0ec89620)
- **Date:** 2026-10-01 · **Mode:** bug, FULL pass (perfection run #5 target)
- **Context pack:** file read end-to-end (753 lines); jCodemunch outline + importers (only `PatternSkin/__init__.py`, names `_film_draw`/`_film_thumbs_ensure`/`_film_thumb_dir`/`_film_fit`/`_film_assign`); the 5 closed remediation rows naming the file (795e1c2 HIGH crashes, FS-1, GROK-FILM5, HY4-FILMCELL-DESELECT, HY4-DRESS-SHARE) loaded as CLAIMS and each re-verified present at the bytes; prior review lineage `ca12e5da` (2026-09-10 FULL re-audit + same-session remediation that PRODUCED these exact bytes - delta since = zero), `e01325dc`, `38811d28`(+r2), `90441958`; deferred-manifest rows; pyflakes + py_compile + the closed-finding pin battery `film_ui_fixes.py` 7/7 GREEN pre-wave.

## Verdict
Shippable; the 2026-09-10 remediation holds at the bytes and no MED+ defect was found. Three LOW findings (wave 1) plus adjudication rows for the previously recorded safeguards. The bytes that shipped since 7e12b526 are exactly the post-remediation bytes this pass started from.

## Bugs & vulnerabilities

**[LOW] PS-FS-GENFALLBACK-SILENT - the genwait seamless-fallback is completely silent** - `PATTERNSKIN_OT_dress_line.modal`, genwait phase (pre-fix line 380)
- What: when `make_seamless`/`_save_gray_png` raises but the raw generated file is still a readable image, the code assigns the raw (deliberate - keeps the paid artifact) with a BARE `except Exception:` - no log line, and the `_done` row says "(generated)" identically to a fully post-processed texture.
- Trigger: any seamless post-process failure with an intact download (e.g. PIL error on an exotic bit depth).
- Impact: the user gets a texture with a visible seam (the exact failure mode the seamless post exists to prevent) with zero signal - not in the log, not in the report, not in the strip.
- Fix (W2): `except Exception as _e:` sets a `seamless_failed` flag, `_log.warning` names the file/error/fallback, and the done-row suffix `", seamless post failed - raw assigned"` appears only when the flag is set. Money-safety contract unchanged (assignment still happens).
- Verification: CONFIRMED (trace; source-level battery rows W2a/b/c, RED pre-fix / GREEN post; mutation m2 caught).

**[LOW] PS-FS-DRESSPARAMS-DRIFT - the dress cache-key/estimate parameters are duplicated at six sites** - lines 178, 194, 207, 232, 267, 311 (pre-fix numbering)
- What: the text-select cache is keyed by (views, threshold); the literals `8` and `0.45` appear in the invoke dry-run cache probe, the G19 cost estimate, the draw() "8 views/clause" label, `self._nv = 8`, and BOTH the modal load and finalize save calls. Any future edit to one site silently re-bills cached matches or misprices the preview.
- Trigger: latent (no current disagreement - all six sites carry 8/0.45 today).
- Impact: money-adjacent drift hazard on a paid path; the dry-run promise ("cached matches are free") breaks if save/load disagree.
- Fix (W3): module constants `_DRESS_NV = 8` / `_DRESS_THR = 0.45` beside DRESS_MIN_SHARE; all six sites reference them; `0.45` appears exactly once post-fix.
- Verification: CONFIRMED (source-level battery W3a/b/c, RED pre-fix / GREEN post; mutation m3 caught on 2 rows).

**[LOW] PS-FS-DEADIMPORT - `_gen_texture_to_library` imported but unused** - pre-fix line 17
- What: pyflakes-class dead name in the `from . import (...)` tuple; zero uses in the module body, zero `filmstrip._gen_texture_to_library` attribute consumers repo-wide (the name stays defined and used in `__init__.py:4339`).
- Fix (W1): removed from the tuple only.
- Verification: CONFIRMED (AST scan W1a1 RED pre-fix naming exactly this name / GREEN post; mutation m1 caught).

## Adjudications (L2.5; contracts_r1.md carries the full rows)
- ADJ-FS-1 `_print_reco` noqa import kept (documented extension hook).
- ADJ-FS-2..5 the four safeguards recorded by the 2026-09-10 audit (dress partial checkpoint; Esc temp-PNG leak round-38 class; stale-triangulation error wording; library walk per clause in invoke) - deferred-LOW ledger rows, none escalated by this pass.
- ADJ-FS-6 pyflakes "forward annotation" cluster on `name: StringProperty(...)`-style annotations = tool noise on the legal Blender idiom (py_compile clean, runtime-proven).
- ADJ-FS-7 dress row hidden rather than greyed when key/sam3 absent = recorded GROK-FILM5 design; G20 grey-vs-hide is an owner design ruling.

## Adversarial verification pass (refuted candidates - deleted per G37, recorded as calibration)
- "`depress`/`sel_on` dead because nothing sets ps_film_sel=1" - refuted: `_ai_select_polypart` (`__init__.py:8371` region) is the only setter and every real select path routes through it (re-confirmed against the 2026-09-10 audit's refutation + current call graph).
- "library_only still bills the AI match per clause" - refuted as a defect: the match is required to LOCATE the part; the invoke estimate line discloses match cost separately from generation cost; product semantics, not a code defect.
- "invoke `_ntris=0` fallback mis-estimates" - refuted: conservative direction only (over-estimates a cached match), preview-only.
- "export `nt == 0` checked after allocations" - waste, not a defect.
- "`film_pick.execute` uses bpy.context.active_object instead of the param" - same object in every reachable path; not a defect.
- "`_dress_parse` splits 'sandblasted' on 'and'" - refuted previously, re-checked: `\band\b` word boundaries hold.

## Remediation postscript (same session)
W1/W2/W3 applied after this review hashed the bytes above; the file is now `b318ff5931703ca3e4bc16acfdb85387272bdd2c2f24468a70d5fc4f98556466` (sha8 b318ff59). Battery `tests/test_perfection_filmstrip.py` 20/20 (RED-first proven, 3/3 mutants caught); full suite 33/34 with only the characterized `test_hunt_r5_fixes.py` pip-bpy native flake (passes standalone). Rows PS-FS-DEADIMPORT / PS-FS-GENFALLBACK-SILENT / PS-FS-DRESSPARAMS-DRIFT in `docs/remediation_manifest.json`, same commit.
