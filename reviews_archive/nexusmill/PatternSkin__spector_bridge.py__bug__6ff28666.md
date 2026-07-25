# BUG review: PatternSkin\spector_bridge.py

- source: `C:\Users\User\source\repos\Nexusmill\PatternSkin\spector_bridge.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:02
- tokens: in 4730 / out 2552
- est cost: $0.0525

---

## Verdict
Not safe to ship as-is. The biggest risk is silent failure combined with false-positive matching: every error path is swallowed by bare `except Exception`, and degenerate (all-zero) DNAs compare as distance 0, which the "strict" gate treats as a guaranteed same-part match — causing a wrong paid scan to be auto-loaded with full confidence.

## Bugs & vulnerabilities

**[HIGH] All-zero DNA produces a guaranteed false "same part" match** - `lines 91-95, 169`
- What: If `eigsh` returns only near-zero eigenvalues (or an empty/degenerate spectrum), `vals` becomes empty after the `vals > 1e-9` filter and `shape_dna` returns `np.zeros(k)` with no error. `dna_distance(zeros, zeros) == 0.0`, which passes `bd <= strict` (0.012) trivially.
- Trigger: Two distinct small/degenerate parts (e.g., nearly planar or fragmented meshes whose spectra get fully filtered, or any mesh where the shift-invert solve at `sigma=-1e-5` on the singular cotan Laplacian returns garbage that gets filtered). Note line 89 solves with `sigma` near the known-zero eigenvalue of `L`, which is numerically fragile — exactly the condition that yields junk eigenvalues.
- Impact: `find_part`/`find_object` report `same_part=True` for unrelated geometry and auto-load an unrelated saved scan "with no SAM cost" — silent data corruption of the user's project, directly contradicting the "GUARANTEED to be the same part" contract in the docstring.
- Fix: After filtering, require `vals.size >= some minimum` (e.g., 8) and `vals[0] > 1e-12`, else raise. Also reject zero-norm DNAs in `find_part`/`find_object` before comparing (`if not np.any(q): return None`), and add a sanity check that `dna_distance` of a vector against the zero vector cannot pass the strict gate.

**[HIGH] Blanket `except Exception: return None` hides all failures, including database and solver errors** - `lines 143-144, 174-175, 190-191, 206-207, 238-239, 266-267`
- What: Every public function catches all exceptions and returns `None`/`0`, indistinguishable from "Spector not installed" or "no match". A corrupted index DB, a locked DB, a SciPy solver crash, or an out-of-bounds face index in user-supplied `F` all vanish silently.
- Trigger: Any transient failure — e.g., `sqlite3.OperationalError: database is locked` (two Blender instances or threads indexing concurrently), or malformed `F` with indices `>= len(V)` raising `IndexError` at line 44.
- Impact: Users lose indexed parts without any signal; the "changed since scan" safety warning (the module's core value) silently never fires; debugging in the field is impossible.
- Fix: Catch narrow exception types (`sqlite3.Error`, `RuntimeError` from `shape_dna`), log the exception via the add-on's logger, and distinguish "no index" from "index error" in the return contract (e.g., return a dict with an `"error"` key).

**[MEDIUM] Re-indexing is non-atomic and can leave the index empty or partial** - `lines 189-208`
- What: `index_scan` DELETEs all rows for `mesh_sig` on one connection, closes it, then re-inserts parts one-by-one via `store_part`, each opening its own connection. A crash (or exception swallowed at line 206) between the delete and the inserts leaves zero/partial rows for that mesh. Concurrently, `find_part` running during the window sees an empty index and returns `None` even though scans exist.
- Trigger: Crash/exception mid-reindex, or two concurrent scans of the same mesh.
- Impact: Permanent silent loss of fingerprints for a mesh; missed matches → wasted SAM cost; flaky behavior under concurrency.
- Fix: Do the DELETE and all INSERTs in a single transaction on one connection (compute DNAs first, then `with db:` delete + executemany). Consider `PRAGMA journal_mode=WAL` for concurrent reader/writer access.

**[MEDIUM] No integrity/format validation of DNA blobs read back from sqlite** - `lines 162, 257`
- What: `np.frombuffer(r[5], np.float64)` trusts the blob blindly. If the DB is corrupted or written by another tool (the file lives in the shared `~/.spector` home, writable by anything), a blob whose length isn't a multiple of 8 raises (swallowed → whole match fails), and a length-0 blob combined with the zero-DNA issue above yields distance 0. `dna_distance` also silently truncates to `min(len(a), len(b))`, so a truncated blob of a *different* part can spuriously match on its prefix.
- Trigger: Corrupted/externally-modified `patternskin_part_index.db`.
- Impact: Wrong-part matches or total match failure with no diagnostics.
- Fix: Validate `len(blob) == 50 * 8` (and version the row format); reject mismatched-length DNAs instead of truncating in `dna_distance`.

**[LOW] `spector_home()` creates `~/.spector` as a side effect of a read-only-looking query** - `line 34`
- What: Merely importing the module and calling `spector_home()` (done by every `_open`/`_index_path` call) creates a directory in the user's home if the `spector` package is importable, even if Spector was never run.
- Impact: Unexpected filesystem mutation; on read-only home dirs `os.makedirs` raises — caught at line 35 only for `find_spec`, so an `OSError` from `makedirs` actually propagates... it is inside the same `try`, so it's swallowed and `None` is returned — behavior differs by failure mode with no logging.
- Fix: Create the directory lazily in `_open()` only when actually writing.

**[LOW] `datetime.datetime.utcnow()` is deprecated and naive** - `lines 141, 236`
- What: Emits `DeprecationWarning` on Python 3.12+; naive timestamps make cross-timezone staleness reasoning unreliable.
- Fix: `datetime.datetime.now(datetime.timezone.utc).isoformat()`.

## Missing safeguards
- Test that a degenerate/single-component tiny mesh never produces an all-zero DNA that passes the strict gate (regression test for the HIGH finding).
- Input validation on `F`: check `F.min() >= 0` and `F.max() < len(V)` before use in `shape_dna`/`geom_sig`, with a clear error instead of a swallowed `IndexError`.
- Logging of every caught exception (module-level `logging.getLogger(__name__)`), at minimum at debug level.
- A uniqueness constraint (e.g., `UNIQUE(mesh_sig, part_id)` on `ps_parts`) so duplicate `store_part` calls for the same part can't accumulate stale duplicate rows — currently only `index_scan` dedupes; direct `store_part` callers can insert duplicates that change "best match" nondeterministically (ties broken by row order, line 164 uses strict `<`).
- A test for the reindex-atomicity window (delete-then-insert) and for concurrent `find_part` during `index_scan`.
- Validation that `scan_path` exists/is readable before returning a `same_part` match, so a "guaranteed" match doesn't hand the caller a dangling path.