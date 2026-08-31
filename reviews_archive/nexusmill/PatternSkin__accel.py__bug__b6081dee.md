Source: PatternSkin/accel.py
Reviewer: claude-sonnet-5 (in-session)
sha256: b6081dee2b9dd0eee4b7055c4d25aaa7766956735b221c628fdf8473d3e86e8d
Date: 2026-07-27
Mode: bug
Context pack: diffed 9a0ee6a..c2d2f34 (recommend_accel's off-matrix tooltip branch, _gfx_table's
compiled_but_unsupported_gpus loop, worker_tier_gap's card-pinned check); cross-read
docs/remediation_manifest.json's 2026-07-26 rocm-rdna3-merge entry for accel.py (worker_tier_gap),
severity HIGH, status "fixed" - this is that fix, already logged; re-verifying it's actually on
disk and correct rather than re-reviewing it as new.

## Verdict
Shippable, clean. The one HIGH-severity gap this diff touches (an off-matrix or wrong-vendor GPU
being offered the ROCm install) was already found and fixed this session; re-traced it end to end
and it holds.

## Bugs & vulnerabilities
None found.

## Verified correct (traced, not flagged)
- **`worker_tier_gap()`** now requires `gpu_support(rec.get("gpu_name", ""))[1] == "pinned"` in
  addition to the vendor/platform/python-version test. Traced: an RX 7600 (gfx1102, listed only
  under `compiled_but_unsupported_gpus`) resolves to `("gfx1102", "off-matrix")` via
  `_gfx_table()`, so `[1] == "pinned"` is False and the button correctly stays hidden. An RDNA 2
  card (absent from both `supported_gpus` and `compiled_but_unsupported_gpus`) resolves to
  `("", "")`, same result. An Intel GPU satisfies the vendor test but `gpu_support("")` (Intel
  isn't in either GPU table) also returns `("", "")` - correctly excluded.
- **`_gfx_table()`'s ordering**: `supported_gpus` is processed before `compiled_but_unsupported_gpus`
  within each tier, and the off-matrix write only applies `if k not in table` (no override), while
  the supported-list write overrides on `st == "pinned"` regardless of what was there before. So a
  pinned status always wins even if an off-matrix entry for the same normalized name was written
  first by an earlier tier in the dict. (Not currently reachable with today's single-tier
  manifest, but the precedence is correct if a second tier is ever added.)
- **`recommend_accel()`'s new `elif gfx and tier_st == "off-matrix":` branch**: sits between the
  existing "pinned" and the existing generic "gfx" (planned-but-unpinned) branches in the
  if/elif chain, so it can't be shadowed by either.
