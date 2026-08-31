# Bug review: `asset-forge/forge/userlib.py` — full-file redo (r2)

- Model: claude-opus-5 (in-session)
- Source path: `asset-forge/forge/userlib.py` (creator edition, canonical)
- sha256: `d51070f39d472c829d9bf23a4ce5eabfdc69dbcb7d54c0f2eeeaaa7312e86227`
- Twin parity: `asset-forge-user/forge/userlib.py` byte-identical at the same sha (G23 verified
  this pass) — verdicts apply to the end-user build unchanged.
- Date: 2026-08-11
- Mode: bug
- **Forced full-file redo at an already-reviewed sha.** The 2026-08-10 review
  (`…__bug__d51070f3.md`) is scoped *"(LIB-FLAGGED-1 addition)"* and examined only the new
  `"flagged" in p.parts` filter, returning "Shippable. No defects found." This pass reviews all
  89 lines.
- Context pack: `get_file_outline`; all three consumers located in `app.py` —
  `userlib_list` (`:926`), `userlib_thumb` (`:932`) and the bundle reference resolve
  (`:1035-1039`), whose `None` handling was read in full; `forge/library.data_uri`;
  `docs/remediation_manifest.json` row `unit9-2hc-tail` (2026-07-22, userlib small fixes).

## Verdict

Shippable. The IP-boundary logic the module exists for is correct, and there is no path
traversal: ids are dictionary keys, never decoded back into filesystem paths. One real
concurrency defect: the module-level index is destroyed before it is rebuilt, so a lookup
racing a listing resolves to nothing and a paid run proceeds without the style reference the
user chose.

## Bugs & vulnerabilities

**[MEDIUM] `list_items` wipes the shared index before repopulating it — a concurrent lookup loses the user's chosen style reference on a paid run** — `userlib.py:29-30`
- **What:** `_INDEX` is module-global state shared by every request thread (Flask serves
  concurrently, and generation runs on a background thread). `list_items` begins with
  `global _INDEX` / `_INDEX = {}` and only then walks up to 2000 files across the roots,
  inserting keys one at a time (line 51). For the whole duration of that walk the index is
  empty or partial, and `path_for`, `thumb_uri` and `reference_data_uri` all read it directly.
- **Trigger:** Any `GET /api/userlib/list` overlapping a reference resolve. The window is real
  rather than theoretical because the resolve does **not** happen at request time: `bundle_start`
  hands off to a background thread, and `_userlib.reference_data_uri(rid)` (`app.py:1035`) runs
  inside it — while the UI is free to reopen or refresh the reference picker, which calls
  `/api/userlib/list`. A large library on a slow or network volume widens the window further.
  The same lookup also fails outright after any process restart between listing and generating,
  since `_INDEX` is in-memory only and nothing but `list_items` ever populates it.
- **Impact:** `reference_data_uri` returns `None`, and the whole bundle generates **without** the
  img2img reference the user selected — a paid run that ignores the steering it was asked for.
  **Mitigated, and deliberately so:** `app.py:1036-1039` detects the `None`, sets
  `job["warning"] = "chosen reference image not found - generating WITHOUT a reference"` and
  snapshots the job, under the comment "don't silently ignore paid steering (G19)". So the user
  is told. They are still billed for a set that does not match their intent and will most likely
  regenerate, doubling the spend. That handling is why this is MEDIUM rather than HIGH.
- **Fix:** One line, and it closes the window completely — build into a local dict and swap it in
  at the end (`idx = {}` … `_INDEX = idx` after the walk) instead of clearing the global up
  front. Assignment of a module global is atomic under the GIL, so no lock is needed and readers
  see either the old complete index or the new one, never a partial. Optionally make the index
  self-healing: have `path_for` trigger a rebuild when it misses, so a post-restart lookup
  recovers instead of degrading to "not found".
- **Verification: CONFIRMED.** `_INDEX` confirmed module-global and mutated only in
  `list_items`; all three readers (`path_for` 68-69, `thumb_uri` 72-79, `reference_data_uri`
  82-89) read it with `.get` and return `None` on a miss, with no rebuild fallback. The
  consumer's `None` branch was read directly at `app.py:1035-1039` rather than assumed, which is
  what establishes both the impact and its mitigation.

## Missing safeguards

- **The 2000-item cap truncates silently, and before sorting.** `list_items(roots, limit=2000)`
  breaks out at line 37-38, then sorts at line 64 — so the retained 2000 are whichever
  `rglob` happened to yield first (filesystem order), sorted only afterwards. A user whose
  generated library exceeds 2000 images simply cannot see or select the remainder, and nothing
  says so: the endpoint returns `{"count": len(items)}`, which reads as a total. Reachable over
  time — `MAX_COUNT_PER_TYPE` is 200 and a library run covers many types. Return a `truncated`
  flag (and ideally sort before truncating, so the cap is deterministic rather than
  filesystem-order-dependent).
- **`rel` holds an absolute path, not a relative one.** Line 49 is `rel = str(p)` on a path
  built from the root, so the id is base64 of the **absolute** local path. Harmless for a
  local-only desktop app and not a traversal risk (ids are looked up, never decoded into paths),
  but it means ids are machine-specific and break if the library moves, and the variable name
  states the opposite of what it holds.
- **`break` exits only the inner loop.** With multiple roots, hitting `limit` breaks the current
  `rglob` and then re-enters the next root's `rglob` to break again on its first entry. Correct
  output, wasted directory walk; `list_items` is called with a single root today
  (`app.py:926`), so it costs nothing in practice.

## Fixed since last review (delta vs `d51070f3`, 2026-08-10)

The prior round reported no defects and recorded two Phase-3 refutations. Both were re-checked
this pass and **both still hold** — recorded `verified-stale`, not re-litigated:
- `"flagged" in p.parts` cannot false-positive on a directory merely *containing* the substring
  (e.g. `flagged_user`): `Path.parts` splits on separators and membership is whole-segment
  equality. Confirmed.
- A user-chosen custom library type named `flagged` cannot manufacture a `flagged` path segment,
  because `_flat_name`/`_plan_paths` make the type a filename **prefix**, not a folder.
  Confirmed against the current `library_gen._plan_paths` (reviewed as Unit 5 this pass), which
  builds `base = f"{_desc}_{seed}_{job_id}"` inside `heightmap/` or `emblem/` only.
The prior review's scope simply did not extend to `_INDEX`'s lifetime, which is where the one
finding above lives.
