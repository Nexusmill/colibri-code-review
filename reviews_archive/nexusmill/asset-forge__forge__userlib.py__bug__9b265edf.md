# Colibri Review - bug (FULL re-audit) - asset-forge/forge/userlib.py

- **Source path:** `asset-forge/forge/userlib.py` (twin byte-identical)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 30
- **sha256 reviewed:** `9b265edfd004a3265b3afc9b5836a8856cd067d95738fa88dd922646129acda4` (sha8 `9b265edf`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL read (owner ruling: pre-gate audits untrusted)
- **Context pack:** importers app.py:1001 (`list_items([_lib_out()])` on the picker's list route), 1007 (thumb), 1110-1115 (`reference_data_uri(rid)` at bundle start: a None result becomes a job WARNING and the run proceeds and bills); the two prior records (d51070f3, r2) and the "SHARED INDEX DESTROYED BEFORE REBUILD" remediation row loaded as claims - the atomic-swap fix is present (lines 38-39, 76); FLAT LIBRARY / LIB-FLAGGED-1 feature rows.

## Verdict
Clean at the bytes: the index is built locally and swapped atomically, flagged/ and previews are excluded, ids survive non-UTF-8 names, and every reader tolerates a cold or corrupt entry by returning None.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards (cross-file, app.py - the lead's call)
- **Cold index = paid run without the chosen reference.** `reference_data_uri` resolves only through the in-memory `_INDEX`; after a server restart (or before the picker has listed in this process) the Studio's remembered `ref_image_id` resolves to None, and app.py:1113-1115 records a warning and proceeds to bill the whole bundle WITHOUT the steering the user chose. Under the refuse-not-substitute ruling (AF-BUNDLE-ALPHA, 2026-08-25) that should be a 400 before any spend ("the chosen reference is no longer available - pick it again"). Not fixed here: decoding the id (it is base64 of the absolute path) without the index would let a crafted id ship any local image to Replicate, so the index must stay the resolver; the refusal belongs at app.py's bundle_start. Realism: low (the pywebview window re-lists on every load) but the money direction is wrong.
- A directory whose name ends in `.png` is indexed as an item (no `is_file()` check); harmless - the thumb returns None.
- Overlapping roots would list the same file twice (same id, two rows).

## Adversarial verification pass (refuted claims)
- "The index is empty during a rebuild" - built into a local dict, rebound once (the 2026-08-11 fix, present).
- "A permission-denied subfolder aborts the listing" - pathlib's rglob swallows PermissionError while walking.
- "Symlinks let a reference escape the library" - the user's own machine reads the user's own file; the id is only ever minted by the walk.
- "`limit` is per root, not global" - the check is on `len(items)` and fires at the first file of every later root.
- "Non-UTF-8 filenames crash the listing" - `surrogatepass` in `_id`.
- "Flagged images are offered as references" - `"flagged" in p.parts` skips them.
