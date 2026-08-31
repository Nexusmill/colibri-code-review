# Bug review: asset-forge/forge/bundle.py (LIB-FLAGGED-1 additions)

- Model: claude-sonnet-5 (in-session)
- sha256 (final, post-fix): d6ab2547...
- Date: 2026-08-10
- Mode: bug
- Context pack: full `_build_one`/`build_bundle` symbol map already held from writing
  this code this session; no prior review of this file existed. Scope: the new
  quality-floor gate (generate/retry/flag), its interaction with tracer embedding and the
  all-or-nothing abort path, and the flagged-folder relocation.

## Verdict

Not shippable as first written - a real `NameError` on every code path that actually
reaches the flagged-relocation block (`os.path.splitext` called with no `import os` in
this file). Caught and fixed in the same review pass; shippable after the fix.

## Bugs & vulnerabilities

**[HIGH] `NameError: name 'os' is not defined` on any flagged bundle image** -
`bundle.py`, flagged-relocation block
- What: the collision-handling fix (added during this same review, mirroring
  `library_gen.py`'s numeric-suffix convention) used `os.path.splitext(final.name)`, but
  `bundle.py` never imports `os` - it uses `pathlib.Path` throughout instead.
- Trigger: any `_build_one` call whose image fails the quality floor twice (first attempt
  + deterministic-alt-seed retry both degenerate) - i.e., exactly the code path this
  entire feature exists to exercise.
- Impact: would have crashed every bundle run that ever produced a flagged item, turning
  a "keep and flag" feature into an unhandled exception that (per the all-or-nothing
  design) aborts the WHOLE bundle and writes `INCOMPLETE.txt` - the opposite of the
  intended behavior, and worse than the pre-fix silent-skip it was replacing.
- Fix (applied): rewritten using `final.stem`/`final.suffix` (already-imported
  `pathlib.Path` properties) instead of `os.path.splitext` - no new import needed, no
  behavior change from the intended numeric-suffix logic.

## Missing safeguards (bullets)

- None outstanding. The all-or-nothing abort semantics were verified correct: a quality-
  floor failure never calls `stop.trip()` (confirmed by reading every path from
  `_generate_once`'s exception handling up through the outer `except BaseException`),
  so only genuine provider/IO errors still abort the bundle - quality-floor rejection
  and its retry are fully contained within the normal successful-return path.

## Fixed since last review

N/A - supersedes `asset-forge__forge__bundle.py__bug__ebe90169.md` (the pre-fix sha),
same review session, not a separate later pass.
