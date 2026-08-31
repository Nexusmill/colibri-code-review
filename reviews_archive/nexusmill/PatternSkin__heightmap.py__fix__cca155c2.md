# Colibri fix-pass record - PatternSkin/heightmap.py (GROK-HM residuals #5-8)
- source: PatternSkin/heightmap.py
- model: claude-fable-5 (in-session)
- sha256: cca155c22a2ca59311c2a8285488fd24822dd98ec2353027cb8ebff6c5228263
- date: 2026-08-15
- mode: fix
- context pack: current-bytes re-baseline (docket sha 151d9bc6 stale post-tranche-2, all
  four residuals still present at 549c21ae); _rasterize_svg white-ground behaviour confirmed;
  HM-PS-NORM percentile stretch left untouched downstream of the new composite.

## Verdict
All four residuals fixed and battery-verified (6/6, real headless Blender, PIL twin-image
comparison for the alpha composite). See remediation row grok-hm-residuals.

## Fixed since last review
- GROK-HM #5 alpha discarded -> straight-alpha composite on white before luma
- GROK-HM #6 float-mtime cache key -> st_mtime_ns + st_size
- GROK-HM #7 unclamped seamless margin -> half-tile clamp + degenerate no-op
- GROK-HM #8 _save_gray_png datablock leak -> new-inside-guard
