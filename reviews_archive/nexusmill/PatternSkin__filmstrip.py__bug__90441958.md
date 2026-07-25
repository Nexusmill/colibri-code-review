# BUG review: PatternSkin\filmstrip.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\filmstrip.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 21:12
- tokens: in 10667 / out 3066
- est cost: $0.0780

---

## Verdict
Mostly shippable UI code, but the export operator has a real format/extension mismatch and an unguarded `written[0]`, and several error paths either swallow failures silently or let unexpected exceptions escape. Biggest single risk: exporting a 3MF-variant (`3MF_FACECOLOR`/`3MF_OBJECTS`) via a default `.stl` filepath produces a mislabeled/mis-named output file, with no extension correction in `execute`.

## Bugs & vulnerabilities

**[HIGH] Wrong default extension and no extension fix-up for 3MF variants** - `line 313`, `line 338`
- What: `invoke` computes the suggested filename as `.3mf` only when `self.fmt == "3MF"`, otherwise `.stl` — so `3MF_FACECOLOR` and `3MF_OBJECTS` default to `parts.stl`. In `execute`, the `.3mf` extension is only force-appended when `self.fmt == "3MF"`; the other two 3MF formats get no correction. The enum's `default="3MF"` is applied at registration, but `invoke` uses the *current* `self.fmt`, which for a freshly-invoked operator is fine, yet any fmt switch after the file dialog (or redo from the F9 panel) hits this path.
- Trigger: choose "3MF - standard face colours" or "3MF - object per part", accept the suggested filename (`name.stl`), export.
- Impact: a 3MF (ZIP) payload written to a `.stl` file — slicers reject it or misparse it; silent wrong-format output.
- Fix: in `invoke`, use `".3mf" if self.fmt.startswith("3MF") else ".stl"`; in `execute`, apply the same `startswith("3MF")` test for the extension fix-up (and conversely append `.stl` for STL format).

**[MEDIUM] `written[0]` IndexError when export returns an empty list** - `line 345`
- What: the success report unconditionally indexes `written[0]`.
- Trigger: an STL export where every part id is negative/unassigned (e.g. stale `ps_ai_part` attribute passes `poll` but `_ai_polypart_read` yields all `-1`), or any `export_parts` path that legitimately writes nothing.
- Impact: unhandled `IndexError` traceback after a *successful* export — the user sees a crash, not a report.
- Fix: `if written: ... else: report warning "Nothing exported"`.

**[MEDIUM] `film_generate.execute` catches only `RuntimeError`** - `line 432`
- What: `_gen_texture_to_library` can raise network, filesystem (`OSError`), keyring, or decoding exceptions; only `RuntimeError` is caught. Compare with `dress_line`, which wraps worker exceptions broadly.
- Trigger: any non-RuntimeError failure during generation (disk full writing to the library, `requests` connection error, invalid token type error).
- Impact: raw traceback out of the operator instead of the `self.report({"ERROR"}, ...)` path; `s.film_edit` is left open and `s.last_error` stays empty.
- Fix: `except Exception as e:` (keeping `RuntimeError` handling identical) and set `s.last_error`.

**[MEDIUM] `tri_part.max()` crashes on an empty triangle mesh; negative part ids leak into the palette** - `line 334`
- What: `pal = _ai_palette(int(tri_part.max()) + 1)` raises `ValueError: zero-size array to reduction` if the mesh has no loop triangles (`nt == 0` — e.g. a mesh with loose vertices only, which still passes `poll` since the attribute exists). Separately, part id `-1` (unassigned triangles, explicitly filtered out elsewhere at line 117) is used to index `pal[i]`/`colours` downstream via `tri_part`; `colours` has no `-1` key and negative numpy indexing would silently wrap to the last palette colour.
- Trigger: empty/degenerate mesh, or a scan that left some polygons at `-1`.
- Impact: unhandled exception, or unassigned triangles silently painted with an unrelated part's filament colour in the exported 3MF — a real multi-material print defect.
- Fix: guard `if nt == 0: report and return {"CANCELLED"}`; either clamp/exclude `tri_part < 0` triangles or assign them a dedicated neutral colour key.

**[LOW] Deselect in `film_cell` depends on a stale custom property, causing asymmetric toggle** - `line 35`
- What: the toggle-off branch requires `obj.get("ps_film_sel")` truthy, but that flag is only ever set (implicitly) inside `_ai_select_polypart` and cleared here. If the user changes the selection via another tool (or the flag is lost on file reload — custom props persist, but selection state doesn't), clicking the active cell *re-selects* instead of deselecting, despite `depress=True` being drawn (line 583 uses the same flag, so at least UI matches — but the "click again to deselect" contract in the tooltip breaks after reload).
- Trigger: save/reload the .blend with a part active, click the active cell.
- Impact: operator behaves opposite to its description; minor UX/logic inconsistency.
- Fix: treat "same part clicked" as toggle-off regardless of the flag, or re-derive the flag from the actual face selection.

**[LOW] Silent failure of the seamless post-process hides a broken output** - `lines 241-245`
- What: `try: _save_gray_png(make_seamless(load_heightmap(out, ...))) except Exception: pass` — any failure (corrupt PNG from the model, OOM in numpy, bad image) is swallowed and the raw, possibly invalid file is assigned to the part anyway (line 246).
- Trigger: Replicate returns a non-image body saved to `out`, or `make_seamless` fails on a degenerate image.
- Impact: the part gets a pattern path that will fail later at Bake with a confusing error far from the cause; user is told "generated" successfully.
- Fix: on exception, verify `out` is still a decodable image; if not, move it to `_skipped` and do not assign.

**[LOW] Unlocked cross-thread result handoff in `dress_line`** - `lines 177-180`, `226-231`
- What: worker threads write `self._res`/`self._err` while the modal timer reads them with only `is_alive()` as synchronization. CPython's GIL makes the reference assignments atomic in practice, but there is no `join()` before reading, and `is_alive()` returning False does not formally guarantee visibility of the writes (no happens-before edge without a lock or join).
- Trigger: non-CPython builds or future refactors; extremely hard to hit on stock Blender.
- Impact: theoretical stale-read of `_err=None`/`_res=None`, which would silently skip assigning a mask (line 193) with no error recorded.
- Fix: `self._thread.join()` (it has already finished when `is_alive()` is False, so this is free) before reading `_res`/`_err`.

## Missing safeguards

- `film_apply_all` (line 63) and `_film_assign` never validate that `part < s.ai_parts_count`; a stale `ps_part_patterns` entry for a part index that no longer exists (after "Fewer parts") survives export/bake and is never cleaned up. Add a pruning pass when the part count changes.
- `_dress_find_library` walks the entire library tree per phrase with no depth/size cap and no symlink guard — a huge or symlinked library dir makes the modal UI stutter; also no test covers descriptor-to-file matching. Cache the file list once per `dress_line` run.
- `_dress_parse` has no tests; e.g. `"knurled grip and plain guard"` relies on `re.split(r"\band\b")`, so a descriptor containing "and" ("black and white blade") is silently split into two bogus phrases. Unit tests for the heuristic are needed.
- `PATTERNSKIN_OT_export_parts.execute` doesn't check that the target directory is writable before doing the (potentially expensive) world-space vertex transform; fail fast on `os.path.isdir(os.path.dirname(fp))`.
- No guard against `s.layer_mm`/`s.nozzle_mm` being negative in `_film_fit` — `layer <= 0` is treated as "rule disabled" (line 285), so a negative printer setting silently disables fitness checks instead of being flagged as invalid configuration.
- `film_cell` line 41: `foreach_set("select", ...)` is called without verifying `me.polygons` count matches after an in-flight mesh edit; a length mismatch raises inside an operator with no try/except.