# Bug review: asset-forge/app.py (LIB-FLAGGED-1 additions, this round)

- Model: claude-sonnet-5 (in-session)
- sha256: 2d557bd3...
- Date: 2026-08-10
- Mode: bug
- Context pack: `detect_legacy_library_folders`/`migrate_legacy_library_folders`/
  `library_types`/`_MODE_DIRS` symbol map already held from writing this code this
  session. Scope limited to the `_LIB_EXTRA` constant and its three call-site exclusions
  added this round - the `/api/library/legacy_folders` and `/api/library/migrate_legacy`
  routes themselves were added and reviewed in a prior, already-committed session.

## Verdict

Shippable. No defects found - three call sites correctly updated to exclude `_LIB_EXTRA`
alongside `_MODE_DIRS`, and `migrate_legacy_library_folders`'s belt-and-suspenders refusal
is redundant-by-design with `detect_legacy_library_folders`'s exclusion (traced: `valid`
can never contain `"flagged"` since it's built from the already-filtered detector output),
which is the intended defense-in-depth, not dead code.

## Bugs & vulnerabilities

None found.

## Missing safeguards (bullets)

None - `library_file()` (the user-driven manual filing endpoint) was checked and
confirmed to still coerce any non-`_MODE_DIRS` mode value (including a hypothetical
`"flagged"`) down to `"heightmap"`, so a user cannot manually file into `flagged/` via
that path either.
