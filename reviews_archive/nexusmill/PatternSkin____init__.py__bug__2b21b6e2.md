# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 14:33
- tokens: in 190623 / out 29295
- est cost: $0.1084

---

## Verdict
After the round‑8 remediations this file is broadly safe to ship, but one new defect stands out: the paid AI multiview‑scan path dereferences `self._res[0]` without the `self._res` guard that the three sibling paths use, so a "no masks" response from SAM‑2 aborts a billed scan with a cryptic `NoneType` error and re‑bills the view on resume. Everything else is either fixed or minor residual cleanup on error paths.

## Bugs & vulnerabilities

**[MEDIUM] `ai_parts.modal` dereferences `self._res[0]` unguarded — a None SAM‑2 result aborts a paid scan and re‑bills on resume** - `line 7823`
- What: in the `wait` phase, after the `if self._err:` block returns, the code does `self._ap.assign_view(self._job, self._i, self._res[0])` with no check that `self._res` is non‑None. The worker `_work` (7777–7782) sets `self._res = self._ap._sam2_masks(...)`; if that returns `None`/empty *without raising* (so `self._err` stays `None`), `self._res[0]` raises `TypeError`. The three sibling paths all guard this exact dereference: `wait_sdf` at **7849** (`if not self._err and self._res`), `sel_text` at **8088** (`if self._res is not None`), and `ai_parts_semantic` at **8344** (`if self._res is not None`). Only this one is unguarded.
- Trigger: run **AI Parts (multiview scan)**; on any view where the SAM‑2 call succeeds but yields no masks (empty/None result rather than an exception).
- Impact: the outer `except` (7920) turns it into `"AI Parts error: 'NoneType' object is not subscriptable"`, `_end(CANCELLED)` aborts the whole scan, and because the crash happens *before* `save_scan_partial` (7837) the current view is not checkpointed — a resume re‑renders and **re‑bills** that already‑paid view. The user loses a paid run to a cryptic message.
- Fix: treat a falsy `self._res` exactly like a missed vote (the `if self._err:` branch already models this): `if self._res: self._ap.assign_view(self._job, self._i, self._res[0])` (and only then advance/`assign_view_sdf`), or fold it into the streak/miss handling and checkpoint past it.

**[LOW] `_punch_holes` leaks `bm_csink` (and `cme` on one path) when `_apply(bm_through)` raises — the "single‑owner" free design doesn't cover the cross‑call error path** - `line 4380`
- What: `bm_through`/`bm_csink` are both created up front (4322–4323). `_apply` frees the `bm` it is handed in its own `finally` (4347–4348), and the `else` branches (4382–4387) free the unused one — but only if execution reaches them. If `_apply(bm_through)` (4381) raises at any point, control jumps past `if use_csink: _apply(bm_csink)` / `else: bm_csink.free()`, so **`bm_csink` is never freed**. Additionally, if the raise happens inside `bm.to_mesh(cme)` (4345), the just‑created `cme` (4344) is orphaned because the `cme`-removal `finally` is later in `_apply` and never reached. This is the exact cross‑call leak the prior review asked to close with a `finally` around the two `_apply` calls; the round‑8 "single‑owner" change closed the per‑call leak but not this one.
- Trigger: **Create scale pair** / **Create scales from outline** with `countersink=True` (so both `use_through` and `use_csink` are set) on a mesh where the through‑boolean fails (degenerate cutter / EXACT‑solver error / OOM).
- Impact: a `BMesh` (and possibly a `PS_ScaleCut` mesh datablock) leaks per failed run — delayed/soft leak until GC, but it accumulates across retries and the `scale_from_outline` caller swallows the error (`except Exception: pass`, 4504), so it is silent.
- Fix: wrap the two calls in one `try/finally` that frees whichever `bm` was not consumed, e.g. `try: ... if use_through: _apply(bm_through) ... if use_csink: _apply(bm_csink) ... finally: [free any of bm_through/bm_csink not yet freed]`; and move `cme`'s removal into the same `finally` that owns `bm.free()` so a `to_mesh` failure can't orphan it.

## Missing safeguards
- The `wait` phase of `ai_parts.modal` should apply the same `self._res` truthiness guard used at 7849/8088/8344; add a test that injects a None/empty `_sam2_masks` result and asserts the scan treats it as a missed vote (checkpoint advances, no `TypeError`, no re‑bill on resume).
- `_punch_holes` needs a single teardown `finally` around both `_apply` calls that frees `bm_through`/`bm_csink`/`cme` on *every* exit; add a test that a forced `_apply(bm_through)` failure leaves no extra `BMesh`/`PS_ScaleCut` datablocks.
- `_gen_lib_worker` (5734) flattens to `rel.split("/")[-1]`; two manifest entries sharing a basename collide in `heightmap/` and the second silently overwrites the first (its `_sha256_file` then matches only the second). De‑duplicate or namespace the output name.
- `_atomic_write_text` (1421) uses a fixed `path + ".ps_tmp"` name; concurrent/repeated writes can collide and a pre‑placed symlink at that name is followed by `open(tmp,"w")`. Prefer `tempfile.mkstemp(dir=...)` + `os.replace` like the other fetch/install paths.

## Fixed since last review
All six round‑8 findings verified resolved in these bytes:
- **R8‑1 `_punch_holes._apply` exception safety** — the body is now wrapped in `try/finally` (4363–4378) that restores `show_viewport` first, then individually guards removal of `mod`/`cutter`/`cme`; `bm.free()` is single‑owner inside `_apply` (4347–4348). (Only the cross‑call `bm_csink` residual above remains.)
- **R8‑2 shared finish material** — `mname` now hashes `normcase(abspath(pattern_path))` + normalized tile when `use_pattern` (2282–2286), so per‑apply image/scale no longer re‑points another object's material; non‑pattern finishes correctly stay shared.
- **R8‑3 self‑update rollback** — `except BaseException as ce` (1814) with chained `raise ... from ce`, `applied.append` recorded at backup time (1804), `.psnew` always cleaned (1810–1812), and an honest `unrestored` list in the message (1825–1828).
- **R8‑4 ESC containment** — `modal()`'s Esc branch wraps `_ps_on_cancel` in `try/except` (676–681); both batch loops guard each `select_set` (4953–4955, 4966–4968).
- **R8‑5 AI temp‑file ownership** — `_end` now removes `_png` and calls `_cleanup_glb()` (7940–7949 and the three sibling `_end`s), with `cancel()` reduced to pure delegation.
- **R8‑6 decimate rollback** — `modifier_apply` is except‑only removal (481–488), avoiding the dead‑RNA `finally` on success. Promos also landed: `_ai_cache_sig` forces `calc_loop_triangles()` (8881), the relief/part‑map drift `RuntimeError`s (444–446, 9038–9040), and the enforced 4M‑triangle 3MF ceiling (3672–3675).

---

## In-session verification + remediation (2026-09-24, round 9)

Both findings verified. Adversary gate round 9: APPROVE WITH MODIFICATIONS, folded in:
the missed-vote branch normalizes _msg before every [:70]/[:160] slice (the branch assumed
self._err was a string - three None-results would have died at the abort line with a raw
TypeError instead of "FAILED (3 in a row)"); _punch_holes' teardown is ONE widened try
from cme creation with pre-initialized handles (cme/cutter/mod/others - a NameError from
the finally would mask the real exception) and except-BaseException teardown, plus a
call-site is_valid finally owning both bms (a through-failure used to leak bm_csink past
the else-branch entirely).

The probes then caught a REAL infinite loop in my own promo fix before any scan did:
_gen_lib_names' collision loop tested `out[rel] in out.values()` - self-membership, always
true once entered. Rewritten with a taken-set (verified standalone; first-occurrence-keeps-
basename, parent-namespaced collisions, numeric fallback).

Fixes: R9-1 `if self._err or not self._res:` with _msg normalization (a falsy result is a
missed vote: checkpointed past, never re-billed, streak-aborts on 3; the benign zero-mask
(label, 0) tuple still flows to assign_view); R9-2 _punch_holes single-try teardown from
cme creation + call-site bm ownership; promos: _gen_lib_names basename-collision namespacing
(taken-set), _atomic_write_text via mkstemp+fdopen+fsync+except-remove.

Tests: tests/test_hunt_r9_fixes.py 6/6 PASS (source pin for the fold+normalization; forced
depsgraph failure leaves no PS_ScaleCut orphans; structural pin for the widened-try
ownership; naming uniqueness/bare-first; failed-write leaves original byte-identical with
no tmp litter). r1-r8 probes + smoke re-passed. NOT COMMITTED.
