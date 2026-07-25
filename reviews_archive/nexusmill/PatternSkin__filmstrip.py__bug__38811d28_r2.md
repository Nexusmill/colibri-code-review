# colibri-review: PatternSkin/filmstrip.py (round 2, deeper sonnet pass)

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\filmstrip.py`
- model: claude-sonnet-4-6 (in-session)
- sha256: `38811d280481454e41d759b22250204801ef326b67cbfcaaae6cd36c1cba3a68` (unchanged since round 1)
- date: 2026-07-24
- mode: bug (round 2 — round 1 was a shallow haiku pass, both findings refuted)

> **⚠ IN-SESSION VERIFICATION CORRECTION (claude-opus-4-8, Phase 3):** the [MEDIUM PLAUSIBLE] part-0
> finding below is REAL by trace but its **proposed fix is WRONG**. `execute()`'s toggle branch is
> purely `int(self.part) == int(s.ai_parts_active)` (line 38) and does NOT read `ps_film_sel` (the
> comment says that gate was deliberately removed). So setting `ps_film_sel=0` / calling
> `_ai_select_polypart` at the restore sites does NOT change the `0==0` branch. The true root cause is
> a **sentinel collision**: `ai_parts_active` defaults to 0, which is also a valid part index, so
> whenever `ai_parts_active==0` (initial state OR the __init__ restore-to-0 path) clicking cell 0
> always toggles-off and part 0 can't be freshly selected via its own cell until another cell is
> clicked. Correct fix = a "none selected" sentinel (e.g. `ai_parts_active=-1`, property `min=-1`,
> toggle-off resets to -1). That change touches the property def + every `ai_parts_active` read/write
> site and needs live-Blender UI testing, so it is **DEFERRED as FS-1** (docs/deferred_manifest.json),
> NOT fixed here. Also NOTE: this review .md + the manifest were committed by the scanner subagent
> (ae9a3ee) despite a READ-ONLY instruction — a directive violation; the content is benign (no code).
- context pack: jCodemunch `get_file_outline`/`find_importers`/`find_references` on filmstrip.py;
  cross-checked every `self._ap.*` call in the dress-line modal FSM against `ai_parts.py`
  signatures (`text_finalize`, `save_text_select`, `load_text_select`, `text_prepare_job`,
  `render_view_png`, `sam3_mask`, `text_assign_mask`, `estimate_cost`, `render_part_thumbs`) —
  all match; traced `_sel_ctx`/`_ai_polypart_read`/`_ai_select_polypart`/`_ai_palette` in
  `__init__.py`; traced every write site of `ai_parts_active` and `obj["ps_film_sel"]` repo-wide.

## Verdict
No crash/security/money-leak defects found this round. One MEDIUM functional/UX defect
(PLAUSIBLE, not runtime-traced): part 0's filmstrip cell can get stuck permanently reporting
"deselected" and never actually select part 0, after a specific silent-restore code path.

## Bugs & vulnerabilities

**[MEDIUM] Part-0 cell can never be (re-)selected after the silent parts-restore path** —
`PatternSkin/filmstrip.py:32-53` (`PATTERNSKIN_OT_film_cell.execute`), interacting with
`PatternSkin/__init__.py:~674` (a restore branch, `s.ai_parts_active = 0` — a "return 1.0
already showing parts" style lazy-restore of previously-scanned/cached parts on file
reopen — the same code path documented by the comment at filmstrip.py:36-37: "ps_film_sel gate
broke the tooltip contract after a file reload").

- **What**: `execute()`'s only signal for "is this cell currently the selected one" is
  `int(self.part) == int(s.ai_parts_active)` (line 38). `ai_parts_active` is an
  `IntProperty(default=0, min=0)` (`__init__.py:1393`). Several scan/restore code paths set
  `s.ai_parts_active = 0` WITHOUT ever calling `_ai_select_polypart(obj, pp, 0)` — confirmed at
  `__init__.py:674` (`s.ai_parts_active = 0` followed only by `_ai_write_colors`/`_ai_overlay`,
  no `_ai_select_polypart` call), unlike the paired sites at `__init__.py:5741`/`5876`/`5417`
  which DO call `_ai_select_polypart(obj, pp, 0)` right after (and that helper is the only place
  that sets `obj["ps_film_sel"] = 1`, at `__init__.py:6031`).
- **Trigger**: reach a state where `ai_parts_active == 0` but no real selection was ever made
  for part 0 (mesh polygons not selected, `ps_film_sel` unset/0) — the restore-on-reopen branch
  at `__init__.py:674` is the concrete example. Then click filmstrip cell 0.
- **Impact**: `execute()` takes the toggle-OFF branch (lines 38-49) because `0 == 0`, even
  though part 0 was never actually selected. It reports `"Part 0 deselected."` (misleading —
  nothing was selected), and critically **does not change `s.ai_parts_active`**. The next click
  on cell 0 hits the exact same `0 == 0` branch again — cell 0 is now stuck: every click reports
  a no-op "deselected" and the user can never enter the SELECT branch (lines 50-52) for part 0
  by clicking its own cell. (Workaround exists: click any other cell first, which changes
  `ai_parts_active` away from 0, then click cell 0 — now `0 != active` and the select branch
  runs correctly, also finally setting `ps_film_sel=1` via `_ai_select_polypart`.)
- **Fix**: don't infer "already selected" purely from the `ai_parts_active` coincidence with the
  IntProperty's zero default. Either (a) gate the toggle-off branch on `obj.get("ps_film_sel")`
  being truthy as well as the index match (restores the original two-signal check, but see the
  file's own comment about that gate being unreliable after reload — so also (b) at every site
  that sets `ai_parts_active = 0` as a restore/reset (not a real click-selection), explicitly set
  `obj["ps_film_sel"] = 0` too, so the two flags start in an agreed state, OR call
  `_ai_select_polypart(obj, pp, 0)` there as the other three sites already do.
- **VERDICT: PLAUSIBLE** — traced statically end-to-end through both files (property default,
  every write site of `ai_parts_active` and `ps_film_sel`, the exact asymmetric restore branch);
  not run inside Blender this round, so marked PLAUSIBLE rather than CONFIRMED per protocol.

## Missing safeguards
- `PATTERNSKIN_OT_film_cell.execute` has no assertion/consistency check between
  `ai_parts_active` and `ps_film_sel` before deciding toggle direction — the two flags can
  silently diverge (see above) with no user-visible sign anything is wrong beyond a misleading
  report string.

## Refuted (did not report)
- `self._ap.text_finalize(...)` call (filmstrip.py:292/297) looked like it might be calling a
  non-existent attribute (only `finalize_job` initially surfaced in a capped symbol search) —
  REFUTED: `text_finalize` is defined at `ai_parts.py:978` with a matching signature; every other
  `self._ap.*` call in the modal FSM (`load_text_select`, `save_text_select`, `text_prepare_job`,
  `render_view_png`, `sam3_mask`, `text_assign_mask`, `estimate_cost`) was cross-checked against
  its `ai_parts.py` definition and all argument orders/kwargs match exactly.
- ESC-handler file deletion racing the background AI-match thread's read of the same PNG
  (filmstrip.py:236-241, thread started at filmstrip.py:266-274) — REFUTED as a crash risk: the
  `os.remove` is wrapped in `except OSError: pass`; on Windows a delete-while-open collides with
  `PermissionError` (an `OSError` subclass) and is silently swallowed exactly as intended, no
  crash and no double-report of the same error.
- `_dress_find_library`'s unguarded `os.walk(root)` (filmstrip.py:102, called from `invoke()`
  at line 174 with no surrounding try/except) looked like it could raise on a permission-denied
  subdirectory and crash `invoke()` — REFUTED: `os.walk`'s default `onerror=None` silently skips
  directories it can't list; no exception propagates.
- `_dress_find_library`'s "shortest matching filename wins" tie-break (filmstrip.py:108-110) —
  considered as a possible-wrong-file selection bug; this is a deterministic, documented
  heuristic choice (not a crash/None/data-loss path), same category as round 1's refuted
  `_dress_parse` "and"-split heuristic — a design limitation, not a defect. Not reported.
- Per the task brief: did NOT re-raise the two round-1 refuted claims
  (`ps_part_patterns.remove(index)` and `_dress_parse` "and"-split).
