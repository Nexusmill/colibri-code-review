# colibri-review — asset-forge/forge/quality.py (bug, round 1)

- **Source:** `asset-forge/forge/quality.py` (byte-identical twin: `asset-forge-user/forge/quality.py`, G23)
- **Model:** claude-fable-5 (in-session)
- **sha256 (reviewed bytes):** `3646fb9d47c96e142c52cdb2fa321935fcc73b347a4332973f814025a83b3278`
- **Date:** 2026-08-04 · **Mode:** bug
- **Context pack:** created 154e9a40 (2026-07-30) with an unusually honest self-audit docstring
  (floors set strictly below the worst human-accepted image; zero false positives on the
  48-image reference set). Consumer: `library_gen.py` quality-floor block (one paid retry at a
  new seed; second failure keeps the image with a warning). First-ever review.

## Verdict
The gate's philosophy is sound and its calibration story is real, but the `detail` metric is
directionally blind — a crisp axis-aligned pattern reads as "no surface structure" and burns a
paid retry. One MEDIUM, fixed in-session with a measured proof.

## Bugs & vulnerabilities

**[MEDIUM] `detail` measures only vertical gradients — legit striped/planked textures falsely rejected, wasting a paid retry** - `line 63`
- **What:** `detail = np.abs(np.diff(g, axis=0)).mean()` is row-to-row change only. An image
  whose structure runs purely vertically (stripes, planks, corduroy, pinstripe — real catalog
  subject classes) has near-zero row-to-row change and scores ~0 despite obvious structure.
- **Trigger:** measured (`junk/hunt_verify_f14.py`): clean vertical stripes → detail **0.0**
  → rejected ("no surface structure: 0.0 < 4.5"). With realistic sensor noise (σ=4) → 1.4 →
  still rejected. Even the horizontal control scored 3.3 < 4.5 (the 512-resize's antialiasing
  dilutes crisp single-edge patterns), so the floor rejected BOTH orientations of a
  legitimate stripe texture.
- **Impact:** `library_gen` burns one paid retry at a new seed (same subject → likely same
  rejection), then keeps the image stamped with a false `quality_warning` — the customer paid
  twice and is told their good texture is degenerate. Money + trust, bounded per item.
- **Fix (applied):** `detail = max(mean|Δrows|, mean|Δcols|)` — best axis wins. `max()` can
  only raise scores, so nothing the old metric ACCEPTED is newly rejected: the docstring's
  zero-false-positive validation property is preserved by construction. Post-fix measured:
  noisy stripes now PASS (4.6), crisp synthetic stripes rise 0.0→3.3 (still under the floor —
  but a real AI render always carries noise/texture, per the σ=4 case), and the smooth
  gradient the floor exists to catch still FAILS (0.31). Harness AF-QUALITY-FLOOR still PASS.

## Phase-3 refutations (not reported)
- *`saturation` divides by `mx+1e-6`* — guarded; black pixels give 0/ε=0, correct.
- *512-resize uses default resample* — a calibration constant, not a defect; thresholds were
  derived through the same path they are applied.
- *`measure` opens without try* — caller (`check` ← library_gen) wraps the whole attempt in
  its own error ladder; a corrupt PNG fails the item loudly, which is the intended contract.

## Missing safeguards
- The floor thresholds were calibrated against `axis=0`-only scores; if a future recalibration
  happens, re-derive them with the two-axis metric (values can only have risen).
