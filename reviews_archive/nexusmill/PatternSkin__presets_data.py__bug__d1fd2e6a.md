# colibri-review — PatternSkin/presets_data.py — bug (hunt round 1, effort=low)

- **Source:** PatternSkin/presets_data.py · **Scanner:** general-purpose subagent @ claude-haiku
  (low effort) · **Verification:** claude-opus-4-8[1m] (in-session) · cost $0.00
- **sha256 reviewed:** d1fd2e6a1c830c601e38cec2e0930b77aa4043b7c6c67d907fd255751d00d503
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (low pass)
- **Context pack:** no prior review / refuted ledger / remediation rows; consumers at
  `__init__.py:3743-3765` (special keys extracted, then `setattr` in a try/except loop).

## Verdict
Pure data literals with valid structure. No defects. The scanner cross-checked every preset value
against the consuming Blender property's constraints — all pass. Stays active for a higher-effort
round (a null low pass is not proof of cleanliness).

## Findings
None.

## What was verified
- Every finish name (GOLD/SILVER/BRONZE/COPPER/GUNMETAL/BLACK/WHITE/PEARL/NONE) exists in
  `PS_FINISHES`; every projection mode (PLANAR/CYLINDRICAL/SWEPT/SWEPT3D/TRIPLANAR), relief
  (RAISED/ENGRAVED) and `depth_falloff` (RADIAL) is a valid enum.
- Numeric ranges within property bounds: `tile_mm` 6–38 (min 0.5), `depth_mm` 0.12–0.65 (min 0.0),
  `contrast` 1.5–2.4 (min 0.5), `resolution` 0.16–0.30 (min 0.05).
- Structure: all presets are `(name, dict)` 2-tuples; special keys (pattern/color_pattern/
  autofit_tiles/pattern_file) handled before the generic `setattr` loop, which is itself
  try/except-guarded — so even a bad key fails gracefully.
