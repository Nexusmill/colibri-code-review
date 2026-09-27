# BUG review: PatternSkin\__init__.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\__init__.py`
- model: xiaomi/mimo-v2.6-pro
- reviewed: 2026-09-24 08:29
- tokens: in 180677 / out 33292
- est cost: $0.1076

---

## Verdict
Much of the prior batch is genuinely fixed, but the `sel_text` half of the HIGH `cancel()` fix was pasted **after a `return` inside `_sem_price`** and is unreachable dead code — so a force-teardown during *Text select* still locks every AI button for the session. Second-biggest risk: seven modal operators still claim their global run-guard **before** unguarded `event_timer_add`/`modal_handler_add`, the exact strand-the-guard failure that was fixed only in `_ps_start`.

## Bugs & vulnerabilities

**[HIGH] `PATTERNSKIN_OT_sel_text` has no `cancel()` — the F2 fix landed as unreachable dead code** - `line 7784` (class is `line 7605–7770`)
- What: the `cancel(self, context)` body intended for `sel_text` is indented inside `_sem_price`, **after its `return` at line 7780** — a nested, never-executed function (the ast scan independently flags "L7784: unreachable code (follows the return at L7781)"). `ai_parts` (7588), `ai_parts_semantic` (8029) and `ai_parts_native` (8178) all got real class-level `cancel()`; `sel_text` did not. `_ai_begin("Text select")` (7669) is therefore still released only via `_end()`, reachable solely from `modal()`.
- Trigger: start *Select by name*, then File▸New / window close / another modal grabs input before it finishes.
- Impact: `_AI_RUN["op"]` stays claimed → `_ai_guard_poll` greys every AI button for the rest of the session with a tooltip pointing at an Esc that no longer exists; the 0.15 s event timer and `self._png` leak. This is the previously-reported HIGH, only 3/4 remediated.
- Fix: delete the dead block from `_sem_price` (lines 7782–7798) and add `def cancel(self, context):` at class-body indent in `PATTERNSKIN_OT_sel_text` (copy the 8029 implementation). Add the force-cancel regression test — it would have caught this.

**[MEDIUM] Global run-guards are claimed before unguarded modal registration — one WM error strands the guard for the session** - `line 3012/3019`, `3240/3243`, `5547/5552`, `6373/6375`, `7410/7413`, `7669/7671`, `7857/7860`, `8092/8093`
- What: `_ps_start` now wraps `event_timer_add`/`modal_handler_add` in try/except with full cleanup (616–631), but every other modal operator still does `guard = True` → `wm.event_timer_add(...)` → `wm.modal_handler_add(self)` with no guard: `install_accel` (`_INSTALLING` set 3012, registration 3019–3020), `install_ml_worker` (`_ML_WORKER_INSTALLING` 3240, 3243–3244), `generate_default_library` (`_GEN_LIB["active"]` 5547, thread started 5551, 5552–5553), `self_update` (thread 6373, 6375–6376), `ai_parts` (`_ai_begin` 7410, 7413–7414), `sel_text` (7669, 7671), `ai_parts_semantic` (7857, 7860), `ai_parts_native` (8092, 8093). If either registration call raises (window closing, `context.window` invalid, WM teardown) no `cancel()` ever runs and `execute()` has already returned/raised past its own cleanup.
- Trigger: click any of these while the window is closing, or invoke `bpy.ops.patternskin.install_accel()` / `check_updates` from a windowless/`--background` context (where the modal timer never fires at all — `check_updates` 3371 and `install_accel` 3019 then leak the Popen + temp log and report nothing, despite the "nothing fails silently" docstring at 2953).
- Impact: `_INSTALLING` / `_ML_WORKER_INSTALLING` / `_GEN_LIB["active"]` / `_AI_RUN` stay claimed → the corresponding feature is refused with "already running" for the whole session; for `generate_default_library` the daemon thread keeps writing the library with no way to see or cancel it; `install_ml_worker` can end with a fully installed but never-activated worker (`enable_worker_tier`, 3307, is only reached from `_finish`).
- Fix: mirror `_ps_start` 616–631 at each site: wrap the two registration calls in try/except that releases the guard (and stops/removes anything created), then re-raise. Give `install_accel`/`check_updates` a `bpy.app.background or win is None` synchronous fallback like `_ps_start` (569).

**[MEDIUM] Shade-smoothing block drops the user's selection and active object when the op fails** - `line 453`
- What: the new F13 scoping block deselects every other object (455–457), makes `obj` active (454), then runs `shade_smooth_by_angle`/`shade_smooth` (460–463), and only then restores the selection (464–466). All of it is inside one `try` with a bare `except Exception: pass` (467) — so if the shade op raises (its `poll()` fails in a headless/scripted context, or during a teardown), the restore loop is skipped and the user's multi-selection is silently lost. `view_layer.objects.active` is never restored on any path.
- Trigger: run Apply (or `api_apply`) in a context where `bpy.ops.object.shade_smooth*` fails its poll, on a multi-object selection.
- Impact: silent, unreported corruption of the user's selection and active object — the exact class of state damage the block's own comment warns about ("put the user's selection back afterwards").
- Fix: capture `_prev_active = context.view_layer.objects.active`, move the restore loop into a `finally`, and restore the active object there too.

**[LOW] `_apply_finish` falls back to `materials.clear()` when no face is fully inside the region — wipes the user's materials** - `line 2208`
- What: the selected-only branch only returns early when `region.any() and not region.all()` (2208). A partial vertex selection in which *every* face straddles the boundary (`region.any()` is False) — a band narrower than one face at the final subdivision density, or feathered edge strips — falls through to `me.materials.clear(); me.materials.append(mat)` (2215–2216), the exact "silently discarded any materials the user already had" defect the docstring at 2152–2154 says was fixed.
- Trigger: `selected_only` apply with a thin selection band and `resolution` such that no face is fully covered, with `finish` set and pre-existing materials on the mesh.
- Impact: the finish replaces every material slot on the whole model while the relief touched only a band; user materials are destroyed with no warning.
- Fix: when `selected_only` is effective but `region.any()` is False, apply the finish to `region` (all-False = no faces change) or report a warning; never reach `materials.clear()` on this path.

**[LOW] `_check_update` URL guard permits any `http(s)` host — F17 only half-applied** - `line 1482`
- What: `if not _url.lower().startswith(("https://", "http://")): _url = "https://nexusmill.com"` accepts attacker-chosen hosts and plain `http://`; the requested host pin was not applied. `_UPDATE["url"]` is then rendered as a first-party "What's new / Get the update" button (`5148`, `5152`, `6353`).
- Trigger: a compromised/CDN-poisoned `version.json` (or plain-HTTP downgrade) returning `"url": "http://nexusmill.com.evil.tld/..."`.
- Impact: a trusted-looking button opens an arbitrary site; `zip_url` itself is safe (`_verified_fetch` pins scheme + host).
- Fix: `u = urlparse(_url); if u.scheme != "https" or u.hostname != "nexusmill.com": _url = "https://nexusmill.com"`.

**[LOW] `_aa_pool` crops tall-narrow tiles to zero width and crashes the apply** - `line 337`
- What: `k = int(t.shape[0] // (1.6 * spt))` uses height only, then `w0 = (t.shape[1] // k) * k` (340) is **0** whenever the tile is more than ~13× taller than wide (`spt >= 8`). The mean-pooled tile becomes shape `(h, 0)`, and line 357 `float(t.max() - t.min())` raises `ValueError: zero-size array to reduction operation`.
- Trigger: a vertical strip texture (e.g. 128×2048 rope/stripe tile — the UI explicitly advertises rope/stripes) with `target_edge` set.
- Impact: Apply/Preview aborts with a raw, meaningless `ValueError` after subdivision may already have run; the user gets no hint that the image aspect ratio is the cause.
- Fix: `k = max(1, min(k, t.shape[0], t.shape[1]))` and only pool when `k >= 2 and t.shape[0] >= k and t.shape[1] >= k` (guard `w0/h0 >= k`).

**[LOW] `unregister()` frees `_PREVIEWS` but leaves `_ENUM_SIG`/`_ENUM_CACHE` — dead enum icon ids after disable→re-enable** - `line 9184`
- What: `bpy.utils.previews.remove(_PREVIEWS)` (9186) invalidates every cached `icon_id`, but `_ENUM_SIG`/`_ENUM_CACHE` (703–704) are untouched. On re-register of the same module instance, `_library_items` hits `if sig == _ENUM_SIG and _ENUM_CACHE: return _ENUM_CACHE` (904–905) **before** rebuilding previews and returns the stale tuples — the precise failure `_previews_reset` (976–977) exists to prevent.
- Trigger: disable and re-enable the add-on in Preferences without restarting Blender (no module re-import).
- Impact: texture picker renders blank/corrupt thumbnails (labels desynced from icons) until the folder signature changes.
- Fix: in `unregister()`, also set `_ENUM_CACHE = []; _ENUM_SIG = None` (call `_previews_reset()`-equivalent bookkeeping after freeing the collections).

**[LOW] `_live_build` leaks the temp PNG when the image load fails (F11 residual)** - `line 2744`
- What: `os.remove(png)` (2762) runs only after `bpy.data.images.load(...)` / the reuse branch succeeds; `_save_gray_png` (2745) or `images.load` (2758) raising leaves `ps_live_<name>.png` in `bpy.app.tempdir`, and `me.uv_layers`/modifier edits before the raise are not rolled back either.
- Trigger: any decode/IO failure on `_save_gray_png` or `images.load` during *Apply as live modifiers*.
- Impact: temp-file accumulation per failure; a half-built UV layer left on the mesh.
- Fix: `try/finally: os.remove(png)` around 2745–2761.

## Missing safeguards
- The force-cancel test requested last round would have caught the dead `cancel`: assert that after `Operator.cancel()` on `sel_text`, `_ai_busy() == ""` and the 0.15 s timer is gone. (Same assertion still valuable for `self_update`, `install_accel`, `install_ml_worker`, `generate_default_library`.)
- No invariant test that "guard claim ⇒ guarded registration": for every modal operator, registration failure must leave `_AI_RUN`, `_INSTALLING`, `_ML_WORKER_INSTALLING`, `_GEN_LIB["active"]`, `_PS_APPLY_BUSY` empty.
- No `--background` test for `install_accel` / `check_updates` — both currently return `RUNNING_MODAL` into no event loop and never complete.
- No test for a disable→re-enable add-on cycle asserting the pattern icon view still has live `icon_id`s.
- `_apply_finish`: no test for "partial selection, no fully-interior face, pre-existing materials" asserting the materials survive.

## Fixed since last review
Confirmed no longer reproducible against current bytes:
- **F1 path traversal in `send_to_spector`** — `bpy.path.clean_name` (8817) plus the unconditional `_<timestamp>.stl` suffix makes a `..` component impossible.
- **F2 `_AI_RUN` lockout** — real `cancel()` now on `ai_parts` (7588), `ai_parts_semantic` (8029), `ai_parts_native` (8178), each removing `self._png` and falling back to `_ai_finish()`; `self_update.cancel()` (6401, F20) removes its 0.2 s timer and cancels a download-phase update. *(`sel_text` remains open — see first finding.)*
- **F3 `_PS_APPLY_BUSY` strand on registration failure** — `_ps_start` 616–631 closes the generator, stops the timer and releases the guard before re-raising.
- **F4 `check_updates` pipe deadlock + FD leak** — stdout now goes to a `mkstemp` log (3358–3360), read and removed after `poll()` (3385–3390), and `cancel()` (3414–3433) terminates the child and cleans both.
- **F5 user-preset validation** — `_user_presets` sanitizes + dedupes names and drops non-dict rows (1323–1344); `int(cfg.pop("autofit_tiles", 4))` is now wrapped (4908–4911).
- **F6 `_default_library_dir` type guard** — `isinstance(_d, str) and _d.strip()` (790–791).
- **F7 empty-region whole-mesh bake** — `bake_regions` counts and skips zero-vertex regions with a warning (4780–4790).
- **F8 `PATTERNSKIN_OT_grow` zero normal** — length check before `normalize()` (2913–2916).
- **F9 file handles / 100 MB reads** — `with` blocks in `_zip_addon_version` (1581), library hash via streamed `_sha256_file` (5345, 5456); `_sha256_file` itself is chunked (1565–1573).
- **F10 `.glb` leaks** — `try/finally` around both the export (8082–8087) and download/parse (8129–8135).
- **F11 live-image ownership** — `ps_live` tag gate + `reload()` (2751–2760) and `os.remove(png)` on the success path (2762).
- **F13 shade scoping** — active + selection are scoped to `obj` around the shade op (453–466). *(restore-on-error gap remains — see third finding.)*
- **F14 seam-fix disclosure** — failure logs `_log.warning` and writes `s.library_status` (3819–3823).
- **F15 key decrypt per redraw** — `_have_cache` per dialog (3629–3633).
- **F16** — `litho_res` hard-capped `max=2048` (2010); blanket hard caps correctly rejected with rationale.
- **F18 `_punch_holes` multi-user mesh destruction** — `if old.users == 0` before `meshes.remove(old)` (4125–4126).
- **F19 sync-queue recursion** — `_PS_SYNC_QUEUED` trampoline (570–605) converts per-item recursion into an outer `while`, with a `finally` that releases the guard on `BaseException`.
- **F12** remains refuted (`_sam2_masks` raises rather than returning `None`); `_sha256_file`, glb and library-hash paths all verified cleanup-complete on the failure paths tested.

---

## In-session verification + remediation (2026-09-24, round 2)

All 8 findings verified against bytes. The HIGH was REAL: the r1 sel_text cancel() landed as
dead code nested in _sem_price after its return (the r1 insertion anchored on the semantic
class declaration without checking what preceded it). 7 confirmations, 0 refutations this
round; F12 refutation upheld again by the reviewer.

Adversary gate round 2 (same subagent, continued): APPROVE WITH MODIFICATIONS - all folded in:
per-site guard release via each operator's OWN cancel()/_end (the lead's hand-rolled
_ML_WORKER_INSTALLING=False and _GEN_LIB["active"]=False releases would have RE-INTRODUCED the
documented double-run races - caught before code); R2-7 needed the global declaration (else
silently dead, the same failure class as R2-1); R2-5 host allowlist with dot-boundary matching
+ https-only; fail-fast background refusal for install_accel/check_updates (registration
SUCCEEDS headless but the timer never fires - the guard strands by a different mechanism);
ERROR report before every re-raise. Rebuttals upheld: no active-restore in R2-3 (apply's own
end convention), no uv-rollback in R2-8 (pre-existing non-transactional function).

Fixes (18 edits): R2-1 cancel moved to sel_text class level (dead block deleted); R2-2
try/except + cancel()/_end + report + raise at all NINE registration sites (install_accel,
install_ml_worker, check_updates, generate_default_library, self_update, ai_parts, sel_text,
semantic, native) + background fail-fast in install_accel/check_updates; R2-3 selection
restore in finally (capture hoisted); R2-4 thin-band returns None (materials survive);
R2-5 https + dot-boundary host allowlist; R2-6 _aa_pool k bounded by BOTH tile dims;
R2-7 unregister resets _ENUM_CACHE/_ENUM_SIG (with global); R2-8 ps_live png removed in finally.

Tests: tests/test_hunt_r2_fixes.py 13/13 PASS (ast dead-code pin, ast registration-wrap
invariant over all 10 guard classes, class-level cancel() presence, sel_text cancel drive,
host-guard truth table, thin-band materials, tall-narrow tile apply, failed-save png cleanup,
disable->re-enable enum reset). tests/test_hunt_r1_fixes.py re-run 21/21 PASS.
NOT COMMITTED (owner order).
