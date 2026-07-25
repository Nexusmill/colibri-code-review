# BUG review: Spector\warehouse.py

- source: `C:\Users\User\source\repos\Nexusmill\Spector\warehouse.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 21:13
- tokens: in 9837 / out 2798
- est cost: $0.0715

---

## Verdict
Not quite safe to ship: the core store is sound, but several code paths assume parts were always ingested with identical parameters and that blobs/refs are trustworthy — foreign packs and mixed-`k` libraries break it. Biggest single risk: `find()` crashes outright (and dedup silently corrupts data when scipy is absent).

## Bugs & vulnerabilities

**[HIGH] `find()` crashes on mixed DNA dimensions** - `line 300`
- What: `_find_locked` does `np.vstack(mats)` on raw per-part DNA arrays with no padding, while `_ingest_locked` (line 248) correctly pads to `dmax`. If any part was ingested with a different `k` (different `dna_dim`), vstack raises `ValueError: all the input array dimensions must match`.
- Trigger: ingest part A with default `k=50`, part B with `k=20`, then call `find()`.
- Impact: every search fails with an unhandled exception; the library becomes unqueryable.
- Fix: replicate the padding logic from lines 247–248 before vstack, or store a fixed canonical `dna_dim` and reject mismatched `k` at ingest.

**[HIGH] Missing scipy turns dedup confirm into always-pass → silent data loss** - `line 174`
- What: `_chamfer` returns `0.0` when `_KDTree is None`. In `_ingest_locked` (line 253) the chamfer result must be `< 0.02` to dedup; `0.0` always passes. So whenever the DNA distance is under `dedup_eps`, the new part is stored as a pure reference — its geometry is discarded — with no real geometric confirmation.
- Trigger: run on an install without scipy; ingest two parts whose DNAs are within `dedup_eps` but whose geometry differs.
- Impact: distinct parts collapse into one blob; the second part's geometry is unrecoverable (silent failure by design of the return-0.0 fallback).
- Fix: when scipy is unavailable, refuse dedup (treat chamfer as `inf`/skip dedup) rather than returning 0.0, and log a warning at startup.

**[MEDIUM] Self-referential / cyclic `ref_id` from a foreign pack causes infinite recursion** - `line 279`
- What: `_geometry_locked` follows `ref_id` recursively (`V, F = self.geometry(ref)`). `_clean_row` never checks that `ref_id != pid` or that refs are acyclic. A crafted `.spectorpack` row with `ref_id == pid` (or a cycle) imports cleanly.
- Trigger: `import_pack()` of a pack containing a row whose `ref_id` equals its own `id`, then `geometry(pid)` / `reproduce(pid)` / `find(rerank=True)`.
- Impact: unbounded recursion → `RecursionError`/hang (RLock is re-entrant so the lock never releases until the exception); also every rerank that touches the row crashes.
- Fix: in `_clean_row`, reject `ref_id == pid`; in `_geometry_locked`, resolve refs iteratively with a visited-set and treat cycles/missing refs as `None, None`.

**[MEDIUM] Draco decode crashes when DracoPy absent at read time** - `line 61`
- What: `decompress_geometry(data, "draco")` calls `_draco.decode`, but `_draco` is only bound if the import succeeded (lines 26–29); on failure only `_HAVE_DRACO = False` is set, leaving `_draco` undefined.
- Trigger: ingest on a machine with DracoPy (blob stored as `draco`), then open the same library on a machine without DracoPy and call `geometry()`/`reproduce()`.
- Impact: `NameError` on any access to that part — including inside `find()`'s rerank, killing the whole search.
- Fix: guard with `if kind == "draco": if not _HAVE_DRACO: raise RuntimeError("DracoPy required...")` and catch that in `find`'s `ch()` (treat as distance `9e9`).

**[MEDIUM] Missing/orphaned blob crashes geometry instead of returning None** - `line 283`
- What: `_geometry_locked` opens `blobs/<hash>.bin` unconditionally. The import path (lines 491–495) copies blobs only if present and never verifies that a row's `blob_hash` has a corresponding file, nor that file content matches the hash; `delete()`'s GC can also remove a blob that a just-imported foreign row references.
- Trigger: import a pack whose DB references a blob not included in the zip (or whose blob was GC'd as a duplicate name), then `geometry(pid)`.
- Impact: `FileNotFoundError` propagates out of `geometry()`, `reproduce()`, and `find()` rerank — unhandled error path the callers clearly don't expect (they check `Vr is None`, which never happens because the exception fires first).
- Fix: wrap the open in `try/except OSError: return None, None`, and in `import_pack` skip rows whose `blob_hash` has no matching blob (and/or verify sha256 of the blob matches its filename).

**[LOW] Backup retention broken for `keep=0`** - `line 412`
- What: `snaps[:-keep]` with `keep=0` evaluates to `snaps[:-0]` == `snaps[0:0]` == `[]`, so nothing is pruned — the opposite of "keep none".
- Trigger: `backup(folder, keep=0)`.
- Impact: unbounded backup accumulation.
- Fix: use `snaps[:max(len(snaps)-keep, 0)]` or special-case `keep <= 0`.

**[LOW] `import_inbox` silently overwrites and swallows all failures** - `lines 534–536`
- What: `shutil.move(p, done/fn)` overwrites an existing same-named file in `done/` (losing the earlier model), and the bare `except Exception: pass` hides ingest failures entirely — the caller can't distinguish "imported 0" from "everything failed".
- Fix: dedupe target name in `done/`, and collect errors into the returned dict.

**[LOW] `NpzFile` never closed in `decompress_geometry`** - `line 63`
- What: `np.load(BytesIO)` returns an `NpzFile` whose underlying handle stays open until GC; harmless for BytesIO but sloppy, and if the blob path is ever swapped to lazy file loading it leaks fds.
- Fix: `with np.load(...) as z:`.

## Missing safeguards
- No test covering mixed-`k` ingests followed by `find()` (would catch the vstack crash immediately).
- No test for the scipy-absent path asserting dedup is *disabled*, not auto-confirmed.
- `import_pack` does not enforce total decompressed size / member count limits (zip-bomb via `extractall` into tmp can fill the disk before any row validation runs); also no check that `library.db` inside the pack is bounded in size.
- `_clean_row` doesn't validate `ref_id` referential integrity (exists, non-self, acyclic) or that `blob_hash` matches `[0-9a-f]{64}` and a present blob.
- `ingest` has no `IntegrityError` handling on the random `pid` INSERT (retry on collision).
- `ingest`/`find` accept arrays with no shape validation — a 1-D or empty `V` crashes at `V.max(0)` with an opaque numpy error; validate `V.ndim == 2 and V.shape[1] == 3 and len(V) > 0`, and that face indices are within `len(V)` before `thumbnail_png` indexes with them.