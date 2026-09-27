# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 18:24
- tokens: in 190919 / out 18155
- est cost: $0.0988

---

## Verdict
Safe to ship — both previously-reported MEDIUM defects are fixed in these bytes, and no new CRITICAL/HIGH issues surface on re-review. The single biggest residual risk is a narrow data-loss hole in the *new* `make_seamless` guard (an uppercase-extension input still overwrites its own source), which is minor and edge-triggered.

## Bugs & vulnerabilities

**[LOW] `make_seamless` self-overwrite guard is case-sensitive and misses uppercase `.PNG` inputs** - `line 4856-4867`
- What: the R11-1 fix computes `outp = re.sub(r"(_seamless)+$", "", splitext(path)[0]) + "_seamless.png"` and refuses only when `os.path.abspath(outp) == os.path.abspath(path)` (line 4858). `os.path.abspath` does **not** normalize case on Windows, so an input named `X_seamless.PNG` produces `outp == X_seamless.png`, the equality check compares unequal, and `_save_gray_png(b, outp)` (line 4867) writes through to the *same* case-insensitive file — silently replacing the source exactly as the original bug did. The prior finding was fixed only for the exact-lowercase `.png` case.
- Trigger: on Windows, run "Make seamless" on `pattern.png` (creates `pattern_seamless.PNG` if the file was saved/renamed with an uppercase extension), then run "Make seamless" again on that uppercase-ext file.
- Impact: the existing seamless texture is overwritten by a second cross-fade pass with no backup and no `UNDO` (`bl_options = {"REGISTER"}` only, line 4841) — unrecoverable data loss if the second pass degrades the texture.
- Fix: compare with `os.path.normcase(os.path.abspath(...))` (or compare `os.path.splitext` stems + `normcase`) before saving; keep the refuse-and-point-to-original behavior.

## Missing safeguards
- The `make_seamless` regression test only pins the lowercase `.png` re-run; it should also assert that an uppercase-extension (`*.PNG`) already-seamless input is refused (or written to a distinct name) rather than overwritten.
- `_atomic_write_text` (line 1427) leaks the `mkstemp` fd on the rare `os.fdopen` failure path (fd is not closed if `fdopen` raises before the `with` binds). Use `try: os.fdopen(...) except: os.close(fd); os.remove(tmp); raise`. (Resource-leak only, no data loss.)

## Fixed since last review
All four round-10/11 findings verified resolved in these bytes:
- **`make_seamless` self-overwrite (lowercase case)** — now refuses with a WARNING naming the original to re-seam (`line 4858-4865`); first-run behavior unchanged. (See the LOW above for the residual uppercase-ext hole in this fix.)
- **`ReferenceError` on a freed target stranding `kept_original` hidden** — `_a_fail`, `cancel`, `_ps_on_cancel` now split apply-copy cleanup and `kept_original` unhide/re-select into independent `try/except` blocks (`line 2588-2611`, `2617-2632`, `2634-2653`), and the in-place face-count check is `ReferenceError`-guarded (`line 2603-2610`).
- **`_ui_teardown` single-`try` skipped cursor restore on a dead workspace** — `status_text_set(None)` and `cursor_modal_restore()` each in their own `try` (`line 9014-9021`).
- **`_ps_rest_kwargs` not cleared on the subdivision-error path** — now `self._ps_rest_kwargs = None` in that `except` too (`line 707-710`), so a failed subdivision no longer pins `obj` + heightmap arrays on the operator instance.

---

## In-session verification + remediation (2026-09-24, round 12)

The round's one LOW verified (abspath does NOT normcase on Windows - the R11 guard missed
X_seamless.PNG; debug-reproduced, then confirmed the FIXED guard refuses with the input
intact). Safeguard promo: _atomic_write_text closes the raw mkstemp fd on the fdopen
failure path. Round 12 was agent 1's first 0-MED pass; with this data-loss LOW fixed, the
next delta decides the clear per D2.

Tests: the r11 battery extended with the uppercase-extension refusal. Two test-side lessons
on Windows' case-insensitive FS: the renamed .PNG file still 'exists' at the lowercase path,
and the cleanup must remove the file once (same inode), not twice.
