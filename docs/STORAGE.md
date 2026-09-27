# STORAGE.md - what colibri writes, remembers, and archives

> Source of truth: `store.py` (cache + manifest + export), `scanner.py` (ranking), and the
> `reviews_archive/` convention (commit 89efc5f). The design goal everywhere: **completed unchanged reviews can be reused; incomplete attempts retain evidence and cost without granting completed status.**

## `.colibri_reviews/` - the per-project store

Created inside the scanned project. Contents:

- **Immutable review reports:** names combine a readable relative path, a full-path
  identity digest, mode, content hash and attempt identifier. Different sources with the
  same content remain distinct; repeated attempts retain their own report bodies.
  Reports use unique temporary files and atomic replacement.
- **`_manifest.json`** - the memory. Schema:

  ```json
  {
    "<absolute source path>": {
      "rel": "relative/path.py",
      "modes": {
        "bug": {
          "sha": "<full sha256 of the file content when reviewed>",
          "output": ".colibri_reviews/<saved review>",
          "reviewed_at": "YYYY-MM-DD HH:MM",
          "tokens_in": 0, "tokens_out": 0, "cost": 0.0, "complete": true
        }
      }
    }
  }
  ```

  Saves use atomic replacement to avoid exposing partially written JSON. A corrupt
  manifest still loads as `{}` (fail-open for reading), which loses cache credit and can
  cause paid reviews to run again.
- **`_all_reviews.md`** - written by Export: a contents list (file + modes done + total
  recorded spend) followed by every saved review concatenated; missing outputs are noted
  inline instead of failing the export.

Recorded cost uses the provider-reported charge when available; otherwise it uses the
configured token-price estimate. Export and recovery totals sum those recorded values.

Incomplete records carry `complete: false`. A failed retry never replaces an existing
completed mode record; it is retained in the entry's `attempts` history. Replaced
records also remain in that history, and costs and exports include it. Legacy records
without a completion flag retain their existing completed interpretation.

Output references are relative to the reviewed project directory (`base`), the parent
of `.colibri_reviews/`, including when opened from another working directory. Legacy absolute references can be resolved after relocation.
Manifest keys remain absolute source paths. Windows keys are case-folded; POSIX keys
retain case sensitivity. After a project move, an entry's `rel` field can help rebuild
its absolute key at the new project directory, provided it does not conflict with an
existing key. Ambiguous relocation mappings preserve their original absolute identities.
Keys already inside the project are preserved. Windows case variants
combine their mode records; distinct POSIX spellings stay separate. Malformed rows
are skipped without discarding unrelated valid rows.

## Status semantics (what "new / done / changed" mean)

`store.status(manifest, abspath, current_sha, mode)`:
- **new** - this (file, mode) has no completed review.
- **reviewed** ("done" in the UI) - a completed review's saved sha equals the current raw-byte sha.
- **stale** ("changed") - the file's bytes changed since its review; a re-run re-bills,
  and with delta mode injects the previous review ([MODES.md](MODES.md#delta-re-review)).

`modes_done` counts only bug, quality and feature modes that are complete and current for the "All three" (`n/3`) column. The
cache compares each mode's latest completed source hash, so touching mtimes alone does
not invalidate a completed review. Without a completed review for the current bytes, a
file remains eligible for a paid retry even if its bytes are unchanged since an incomplete
attempt.

## Shared between surfaces

The console and `run_batch.py` read and write the SAME store (batch resolves it at the
requested project root (or explicit `--root`)). A batch sweep shows up as `done` in the console; a console
review makes batch print `SKIP`. Batch additionally writes its own copies + summary to
`--out` ([BATCH.md](BATCH.md)). If the summary cannot be written, batch prints recovery
JSON and the recorded total to the terminal; when report persistence also failed, that
JSON includes the paid response and usage.

A completed record identifies the exact source buffer reviewed, using the digest computed
from that same buffer. Later source edits do not change the record; status compares its
digest with the current hash supplied by the caller.

## Scanner ranking

`scanner.scan(root)` walks the tree with hard exclusions - deny-listed directory names
(secrets/legal/media/junk/build/dist/venvs/vendor/caches/IDE dirs...), any subtree
containing `pyvenv.cfg` (a bundled virtualenv), vendored directory components, minified/lock/
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
