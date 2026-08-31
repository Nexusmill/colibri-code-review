Source: PatternSkin/__init__.py
Reviewer: claude-sonnet-5 (in-session)
sha256: 7e53c3158cf82a00d0f2a1b1aead9c0cc2769a1392b1ea2f50dd923ad85ea34f
Date: 2026-07-27
Mode: bug
Context pack: full diff 9a0ee6a..c2d2f34 (308 lines: apply_pattern's per-loop rework,
PATTERNSKIN_OT_install_ml_worker's ensure_python312/self-test wiring, _load_preset's AUTO reset,
mode/batch_mode/region_mode enums, coarse-mode BALL inclusion); cross-read
PatternSkin/accel_bootstrap.py and PatternSkin/projections.py for the functions this file calls
into; checked docs/remediation_manifest.json for the per-loop-UV entry (2026-07-27,
perloop-uv-capaware) confirming apply_pattern's rework is the already-logged fix, not new scope.

## Verdict
Shippable. The per-loop rework and preset-reset fix both hold up under re-tracing. One cross-file
finding (shared with accel_bootstrap.py): `PATTERNSKIN_OT_install_ml_worker.cancel()` clears the
"already installing" guard before the background thread has actually stopped, which is the other
half of the concurrent-`ensure_python312()` race documented in that file's review.

## Bugs & vulnerabilities

**[HIGH, cross-file] `cancel()` clears `_ML_WORKER_INSTALLING` without waiting for the thread** - `PATTERNSKIN_OT_install_ml_worker.cancel()`, line 2797
- What: `cancel(self, context)` sets `self._cancel_event.set()`, then immediately `_ML_WORKER_INSTALLING = False` and tears down the timer — it never checks `self._done` or joins `self._thread`.
- Trigger: Blender invokes a modal operator's `cancel()` in circumstances outside this operator's own Esc handling in `modal()` (e.g. the file being closed, another modal operator forcibly taking over) while the background daemon thread is still inside `ensure_python312()` or `bootstrap_ml_venv()`.
- Impact: the global guard now reads "not installing," so the user (or a re-triggered UI action) can start a second `PATTERNSKIN_OT_install_ml_worker.execute()` while the first thread is still alive. `bootstrap_ml_venv()`'s own lock would eventually serialize the two *inside* that function, but `ensure_python312()` (see accel_bootstrap.py review, same date) has no lock at all — so if either thread is still in that phase, both proceed concurrently against the same `PY312_DIR` staging path.
- Fix: have `cancel()` set the cancel event and mark a "stopping" state, but only clear `_ML_WORKER_INSTALLING` from `_finish()` (already reached once `self._done` is True) or after joining the thread with a bounded timeout.

## Verified correct (traced, not flagged)
- **Per-loop `loop_mask` + partial vertex selection feeding `uv_collapse_ratio`**: worth stating explicitly since it was the first thing I suspected. A face straddling a selection boundary contributes only its selected-vertex loops to `face_of`; `uv_collapse_ratio`'s shoelace/Newell reduction over that non-cyclic subset lands at (near-)zero for both `uv_area` and `geo_area` when only 2 survive (a degenerate 2-gon integrates to zero both ways), and the `real = expect > 1e-12` mask then excludes that face from the ratio entirely rather than injecting noise. For 3+ survivors the reduced polygon still measures a locally-meaningful area ratio. No bug.
- **`_load_preset`'s new `s.mode = "AUTO"` reset on "(none)"**: confirmed this is the correct property. Smart Select (`patternskin.smart_select2`) only selects geometry; the main Apply operator (`PATTERNSKIN_OT_apply`) reads `s.mode`, not `s.batch_mode`/`s.region_mode` (those belong to separate Batch/Region tabs with their own dropdowns, never gated by `obj_preset`). The reported repro ("smart select, then apply, no preset chosen") only ever touches `s.mode`, so this fix is correctly scoped and there is no analogous staleness gap in `batch_mode`/`region_mode` to chase.
- **`h` array shape through the per-loop -> per-vertex transition** (apply_pattern lines 249-325): traced the two branches (`len(Pl)` truthy vs. the "nothing selected carries a face" fallback at line 253) — `u,v,h` stay consistently per-loop-shaped through the tile2 blend and are only ever collapsed back to per-vertex (via the `np.bincount` average) on the branch where they were expanded to per-loop in the first place. No shape mismatch.
- **Coarse-mesh AUTO guard extended to include `"BALL"`** (line ~2191): correct — BALL is exactly the same class of nonlinear-wrap-needs-dense-geometry mode as SPHERICAL/CYLINDRICAL/SWEPT/SWEPT3D.
