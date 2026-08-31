# Bug review: asset-forge/forge/userlib.py (LIB-FLAGGED-1 addition)

- Model: claude-sonnet-5 (in-session)
- sha256: d51070f3...
- Date: 2026-08-10
- Mode: bug
- Context pack: `list_items` symbol map + its one call site (`app.py`'s `userlib_list`,
  feeding the Studio's style-reference picker) already held from writing this code this
  session.

## Verdict

Shippable. No defects found.

## Bugs & vulnerabilities

None found. Considered and refuted: `"flagged" in p.parts` false-positive risk against a
library root whose own ancestor path happens to contain the substring "flagged" (e.g. a
user directory literally named `flagged_user`) - `Path.parts` splits into whole path
segments and membership is exact-string equality per segment, not substring matching, so
`"flagged_user"` never equals `"flagged"`. Also considered: a user manually choosing the
custom library type name "flagged" via `/api/library/file` - traced through
`_flat_name`/`_plan_paths`, confirmed the type becomes a FILENAME PREFIX
(`flagged_something.png`), never a folder, so it cannot produce a `flagged` path segment
either.

## Missing safeguards (bullets)

None.
