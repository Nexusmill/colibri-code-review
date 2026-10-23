# Colibri review — src/jcodemunch_mcp/parser/parse_cache.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\parser\parse_cache.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `e2cc447d8f0fdea0db2ff664a291a1ad8a54183e738e9e12da0a3833aff23c63` (current bytes at dispatch, 2026-09-13; the sub-agent's summary recorded only the first 12 characters - the full digest was taken here and matches that prefix)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted); the whole 167-line module - the docstring's contract ("any read/deserialize failure falls back to a live parse - the cache can never produce wrong symbols, only a slower miss"), `_connect` 96-106 (`mkdir(parents=True, exist_ok=True)` then `sqlite3.connect`), the read path 131-145 (`except sqlite3.Error`), the write path 147-166 (`except (sqlite3.Error, TypeError, ValueError)`); both production callers pass no `source_bytes` (`tools/_indexing_pipeline.py`, `tools/index_folder.py`); `tests/test_parse_cache.py`. No prior `.colibri_reviews` record.

## Verdict
The cache promised "a slower miss, never a crash" and kept it for SQLite failures only; the directory it creates on the way to SQLite could fail with an `OSError` neither path caught, and the indexer crashed on an opt-in cache. Fixed.

## Bugs & vulnerabilities
**[HIGH] `cached_parse_file` raised `OSError` out of the indexer when the configured cache directory was unusable — CONFIRMED — FIXED** - `line 143, 164`
- What: `_connect` runs `Path(d).mkdir(parents=True, exist_ok=True)` before `sqlite3.connect`; a file sitting at `JCODEMUNCH_PARSE_CACHE` (FileExistsError), a file in the middle of the path (NotADirectoryError/FileExistsError) or a permission denial are `OSError`s, not `sqlite3.Error`s, so both the read and the write path let them escape - every parse on every seat pointed at that path crashed, contradicting the module's own contract. Trigger (audit probe, RED on these bytes): a regular file at the cache path → `FileExistsError: [WinError 183]` out of `cached_parse_file`.
- Fix: both except clauses add `OSError`; the read path falls back to a live parse, the write path stays best-effort. Signature and return type unchanged.

## Refuted (recorded so they are not re-raised)
- Cache key excludes `source_bytes` → offset collisions: neither production caller passes it; the docstring scopes the key to content_hash + language + filename.
- `_evict_oldest` + `INSERT OR REPLACE` not atomic across seats: one implicit transaction on one connection, committed once; WAL + `timeout=10` serialises writers and a lock timeout is an `OperationalError` the existing handler catches.

## Adversarial verification (Phase 3)
- Pinned end to end through `cached_parse_file` with `JCODEMUNCH_PARSE_CACHE` pointed at a file, and at a path with a file in the middle: the live parse's symbols come back and the blocking file is not clobbered.
- Controls: a usable cache directory still caches (one row after two calls); an unset variable is a pass-through that writes nothing.
- `tests/test_parse_cache.py` unchanged and green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `24a62be1419483af7112119895e1d56a30e156ee4faca11de66d799226e9c6ba`. TDD: `tests/test_parse_cache_reaudit.py` (4 tests) - 2 RED on the old bytes, 2 controls green throughout, GREEN after. The audit probe passes after.
