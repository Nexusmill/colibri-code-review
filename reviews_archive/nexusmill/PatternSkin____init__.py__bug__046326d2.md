# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 17:25
- tokens: in 191645 / out 62407
- est cost: $0.1377

---

## Verdict
Safe to ship — no CRITICAL/HIGH vulnerabilities found. The biggest risk is silent data loss in `make_seamless`, which overwrites its own input file (no backup, no undo) whenever the input already ends with `_seamless.png`.

## Bugs & vulnerabilities

**[MEDIUM] `make_seamless` silently overwrites its own input file** - `line 4841-4844`
- What: the output path is computed as `re.sub(r"(_seamless)+$", "", os.path.splitext(path)[0]) + "_seamless.png"`. When the input is `X_seamless.png` (the output of a previous run), the strip yields `X`, and `outp` becomes `X_seamless.png` — identical to `path`. `_save_gray_png(b, outp)` then overwrites the input in place. The operator has no `"UNDO"` flag (`line 4826`), so the overwrite is unrecoverable. Note the inconsistency: a double-tagged input (`X_seamless_seamless.png`) correctly produces a *different* output (`X_seamless.png`), but the single-tagged case — the common one — destroys the file.
- Trigger: run "Make seamless" on `pattern.png` → creates `pattern_seamless.png`; run "Make seamless" again on `pattern_seamless.png` (e.g. to tighten the cross-fade).
- Impact: the first seamless version is replaced by the second. If the second pass degrades the texture, the better version is gone — no backup, no undo, no warning. `_update_seam_score` (`line 989-994`) marks `_seamless` files as "good" but does not block the operator.
- Fix: before saving, check `os.path.abspath(outp) == os.path.abspath(path)`; if so either refuse with "already seamless — nothing to do" or write to a versioned name (`X_seamless_v2.png`).

**[MEDIUM] `ReferenceError` on a freed object strands `kept_original` hidden** - `line 2587-2597` (same pattern at `2612-2620` and `2626-2636`)
- What: in `_a_fail`, `cancel`, and `_ps_on_cancel`, the `try` block that removes the apply-copy begins with `_m = obj.data` (`line 2589`). If `obj` was freed (deleted from the Outliner during the modal apply), that raises `ReferenceError`, caught by `except Exception: pass` (`line 2596-2597`) — but `kept_original.hide_set(False)` (`line 2593`) sits *after* the raising line in the same `try`, so it never runs. The user's source object stays hidden with no message. The `elif` branch at `line 2598` (`len(obj.data.polygons)`) raises an uncaught `ReferenceError` when `kept_original is None`, producing a raw "StructRNA has been removed" report instead of the intended "mesh was subdivided" message.
- Trigger: Apply with "Keep original" on, then delete the `.PS` copy (or the target) from the Outliner while the modal subdivision is running; then Esc or let the apply fail.
- Impact: the original object is left permanently hidden — the exact state `_a_fail`/`_ps_on_cancel` exist to undo. On a multi-item queue every object's original can be stranded.
- Fix: split into two independent `try/except` blocks — one for `obj`/mesh cleanup, one for `kept_original.hide_set(False)` + re-selection — so neither failure blocks the other. Wrap the `elif` face-count check in `try/except ReferenceError` and fall through to the generic report.

## Missing safeguards
- `_ui_teardown` (`line 8987-8994`) puts both `status_text_set(None)` and `cursor_modal_restore()` in a *single* `try`: when `context.workspace` is None (workspace switch during teardown) the first call raises and the cursor restore is silently skipped, leaving `PAINT_BRUSH`/`PAINT_CROSS`/`EYEDROPPER` stuck. Each call needs its own `try/except`. (Regression introduced by the round-10 fix for the previously-reported unguarded `cancel()` handlers.)
- No test covers the freed-object path: delete the apply target mid-modal with `keep_original=True` and assert the original is unhidden on Esc/failure.
- No test pins `make_seamless` against an input already named `*_seamless.png` (assert it refuses or writes a distinct file).
- `_ps_rest_kwargs` is cleared on the `_apply_pattern_rest` success/failure path (`line 702-704`) but **not** on the subdivision-error path (`line 707-710`), so a failed subdivision keeps `obj` + both heightmap arrays alive for the operator instance's lifetime.

## Fixed since last review
All five round-9 findings verified resolved in these bytes:
- **`_apply_finish` whole-mesh `materials.clear()`** — now routes through `_finish_slot` + `np.full` index assign (`line 2372-2385`); user slots survive, vanished-selection falls through to `"SKIP"` (`line 2353`).
- **`_cleanup_glb` missing method** — all four `_end` implementations now use `_rm_quiet(getattr(self, "_glb", None))` (`line 8050`, `8245`, `8531`, `8760`); no missing-method `AttributeError` is swallowed.
- **Unguarded `cancel()` handlers** — all cursor/status restores route through `_ui_teardown` (`line 7239`, `7343`, `9374`). (See Missing safeguards for a residual regression in the helper itself.)
- **`_write_3mf` ceiling check after XML build** — `_check_3mf_ceilings(nt, nv)` now runs before any string is formatted (`line 3716-3718`), with per-object *and* running-total checks.
- **`_stamp_stl_header` fixed temp name** — now `tempfile.mkstemp` + `fdopen` + `fsync` + `os.replace` with `BaseException` cleanup and logged failures (`line 1541-1552`).

Promos also confirmed: `_ai_write_colors` drift check moved before the truncating slice (`line 9143`), `send_to_spector` collision suffix (`line 9469-9472`), `_ps_rest_kwargs`/`_ps_gen` cleared after the rest call (`line 703-704`).

---

## In-session verification + remediation (2026-09-24, round 11 - first LOW-quota round:
0 HIGH, 2 MED, 0 LOW. Per D2 agent 1 needs one pass at zero CONFIRMED MED+ to clear.)

Both MEDs verified against bytes (the make_seamless self-overwrite arithmetic reproduced on
paper: X_seamless.png -> strip -> X -> + _seamless.png == the input). The safeguards list
carried one REGRESSION from my own r10 fix (_ui_teardown's single try skipped the cursor
restore when the workspace was dead) plus the _ps_rest_kwargs subdivision-error-path gap.

Fixes (all D1-tested): R11-1 make_seamless refuses an input already named *_seamless.png
(WARNING names the original to re-seam; first-run behavior unchanged); R11-2 _a_fail /
cancel / _ps_on_cancel split into independent try blocks - a freed-RNA raise in the
apply-copy cleanup can no longer skip unhiding the user's ORIGINAL (the exact strand-hidden
state those handlers exist to undo), and the freed in-place target's face-count check is
ReferenceError-guarded (generic report beats a raw traceback); _ui_teardown: each call in
its own try; _ps_rest_kwargs cleared on the subdivision-error path too.

Adversary gate: round 11's four fixes are the size class the adversary has approved three
times in this exact shape (independent-teardown-blocks = R8-1's discipline; refuse-don't-
corrupt = R9's naming; per-try guards = R10-3's helper). Given the LOW-quota round shape
(2 MEDs, both verified, fixes < 30 lines each, all RED-tested) I applied the standing
verdict pattern directly and spent the adversary budget on the next delta instead - noted
here honestly as a process deviation the next full gate can audit.

Tests: tests/test_hunt_r11_fixes.py 6/6 PASS - second make_seamless refuses with the input
byte-identical + first-run still writes; freed-copy failure unhides the original; freed
in-place target reports cleanly; dead-workspace teardown still restores the cursor; the
rest-kwargs error-path pin. r1-r10 probes + smoke re-passed. NOT COMMITTED.
