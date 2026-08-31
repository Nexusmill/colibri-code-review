# colibri gate — asset-forge/forge/quality.py (grok round 6)

- **source:** asset-forge/forge/quality.py (+ asset-forge-user twin, G23)
- **model:** grok-4.3 (external, .grok_reviews/2026-08-22_quality_grok43.md) gated in-session by claude-fable-5
- **sha256:** bb07a93c14744b97... (current bytes at dispatch, G36; matches recorded slate sha)
- **date:** 2026-08-22 · **mode:** bug (grok round 6; first dedicated grok review, prior colibri 3646fb9d/997037b4)
- **context pack:** the floor's role + the r5 GROK-LG5 #1 caller-side wrap + the LIB-LIGHT-GATE deferral pre-declared; verified against measure()/check() source and the library_gen call site.

## Verdict
Shippable; one real MEDIUM silent-mis-score on degenerate image shapes. Grok returned a
single finding, CONFIRMED, no padding.

## Findings after adversarial verification

**[MEDIUM, CONFIRMED — silent mis-score on a 1px-dimension image] `detail` metric goes nan, disabling the detail floor** — `measure()` line 129 (the `detail` expression)
- Traced: `measure` does `im.convert("RGB")`, resizes to 512×512 ONLY when `max(im.size) > 512`, so a small image with a size-1 axis (1×N / N×1 / 1×1 with the other dim ≤512) survives to `g` with a length-1 axis. `np.diff(g, axis=0)` on a 1-row `g` yields shape (0, W); `.mean()` of an empty array is **nan** (with a RuntimeWarning). Then in `check()`, `m["detail"] < MIN_DETAIL` is `nan < 4.5` → **False**, so the "no surface structure" floor NEVER fires, and the returned metrics dict (stored on the item as `quality_metrics`) carries a nan.
- Reachability: a well-formed provider image is never 1px, but the r5 GROK-LG5 context is exactly that a truncated/corrupt PNG can reach the floor; PIL can open a truncated stream as a valid-but-degenerate (e.g. single-row) image. Post-r5 this no longer double-bills (the caller wraps the floor), but the failure mode shifted: instead of crashing it now silently PASSES a structureless degenerate image and pollutes the metrics with nan. `measure` is also public (census/test callers).
- Severity: MEDIUM as Grok rated — narrow trigger, but it defeats a paid-image quality gate silently rather than loudly. Grok's fix is correct and minimal:
  ```python
  d0 = float(np.abs(np.diff(g, axis=0)).mean()) if g.shape[0] > 1 else 0.0
  d1 = float(np.abs(np.diff(g, axis=1)).mean()) if g.shape[1] > 1 else 0.0
  "detail": max(d0, d1),
  ```
  (0.0 for a degenerate axis is correct — a 1px axis genuinely has no along-axis structure — so the detail floor then correctly fires on such an image instead of passing it.)
- Note: the other metrics survive a length-1 axis (`g.mean()`, `np.percentile`, the saturation mean all work); only `detail` breaks. So the fix is localized.

## Refuted and dropped
None — single finding, confirmed.
