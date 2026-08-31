# STORAGE.md - what colibri writes, remembers, and archives

> Source of truth: `store.py` (cache + manifest + export), `scanner.py` (ranking), and the
> `reviews_archive/` convention (commit 89efc5f). The design goal everywhere: **a paid
> review is never lost and never re-billed while the file is unchanged.**

## `.colibri_reviews/` - the per-project store

Created inside the scanned project. Contents:

- **One review file per (file, mode, content-sha):**
  `<flattened-rel-path>__<mode>__<sha8>.md`. Path separators flatten to `__`; the name is
  capped to its last 120 chars (Windows 260-char path limit) while staying unique via the
  sha suffix. Each file opens with a header: source path, model, review timestamp,
  in/out tokens, estimated cost - then the review body. Writes are atomic
  (temp + `os.replace`), so a crash never leaves a half-written review.
- **`_manifest.json`** - the memory. Schema:

  ```json
  {
    "<absolute source path>": {
      "rel": "relative/path.py",
      "modes": {
        "bug": {
          "sha": "<full sha256 of the file content when reviewed>",
          "output": "<absolute path of the saved review>",
          "reviewed_at": "YYYY-MM-DD HH:MM",
          "tokens_in": 0, "tokens_out": 0, "cost": 0.0
        }
      }
    }
  }
  ```

  Saves are atomic for a hard-learned reason: a crash mid-dump once corrupted the
  manifest, `load_manifest` fell back to `{}`, and the whole project's sha cache + cost
  ledger silently reset - every file re-billed as new. A corrupt manifest still loads as
  `{}` (fail-open for reading), but can no longer be produced by a crash mid-write.
- **`_all_reviews.md`** - written by Export: a contents list (file + modes done + total
  recorded spend) followed by every saved review concatenated; missing outputs are noted
  inline instead of failing the export.

## Status semantics (what "new / done / changed" mean)

`store.status(manifest, abspath, current_sha, mode)`:
- **new** - this (file, mode) was never reviewed.
- **reviewed** ("done" in the UI) - the saved sha equals the file's current sha.
- **stale** ("changed") - the file's bytes changed since its review; a re-run re-bills,
  and with delta mode injects the previous review ([MODES.md](MODES.md#delta-re-review)).

`modes_done` counts how many modes are current for the "All three" (`n/3`) column. The
cache is keyed by CONTENT sha, so touching mtimes, re-cloning, or reverting a change all
resolve correctly - only real byte changes cost money again.

## Shared between surfaces

The console and `run_batch.py` read and write the SAME store (batch resolves it at the
reviewed files' common base). A batch sweep shows up as `done` in the console; a console
review makes batch print `SKIP`. Batch additionally writes its own copies + summary to
`--out` ([BATCH.md](BATCH.md)).

## Scanner ranking

`scanner.scan(root)` walks the tree with hard exclusions - deny-listed directory names
(secrets/legal/media/junk/build/dist/venvs/vendor/caches/IDE dirs...), any subtree
containing `pyvenv.cfg` (a bundled virtualenv), vendored path substrings, minified/lock/
map/bundle files, files over 2MB - then scores each survivor from 100:
depth (-6/level), very dense sibling dirs (-15/-40/-80 at >30/>60/>150 files = vendored
bundle smell), core names like `app.py`/`main.py`/`core.py`/`index.ts` (+15), primary
code extensions (+8, css/html -6), tiny files (-20), a real header/import at the top
(+4). Rows carry path, rel, ext, chars, estimated tokens (`chars/3.5`), sibling count,
score, and the content sha; sort is score-then-size descending. The console's "Hide
vendored / low-signal" filter is simply `score < 40`.

## `reviews_archive/` - colibri's own durable copy (the memory feature)

`.colibri_reviews/` lives in the SCANNED repo, where it can be moved, cleaned, or
gitignored by that repo's owner. `reviews_archive/<repo-slug>/` in THIS repo keeps
colibri's own committed copy of every review it has written into another repo's working
tree, plus that repo's manifest - durable, and it travels with colibri.

The same scans are indexed into this repo's memory store (`.repo-memory.json` carries the
autoindex config, so indexing happens on server start and on reads) as scan history plus
one campaign roll-up per repo (files covered, modes, models, cost, date span). Refresh
after new scans:

```bash
C:\Users\User\source\repos\repo-memory\.venv\Scripts\python.exe -B -m repo_memory.colibri --repo <path> --mirror
```

Convention note: archive manifests may carry synthetic mode keys beyond the five review
modes (e.g. `gate`, `debug`, `ultra-gate` rows written by review sessions) and
`sha_partial: true` where only a short sha was recorded - the archive is a ledger of
what happened, not a cache, so nothing validates against `MODES` there.
