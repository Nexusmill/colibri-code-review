# Colibri review — src/jcodemunch_mcp/evidence/scip.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\evidence\scip.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `c4002eb8f884c7f3e4deda17e70c76295754d16f84033021c574d37a4f87d100` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 3 refuted); `parse_scip_file` 270-276 (`read_bytes` then `gzip.decompress`, both unbounded) and `parse_scip_bytes` 239-267 (the only ValueError contract); the single production chain `tools/import_scip.py::import_scip` → `scip_ingest.ingest_scip_file` → `parse_scip_file` (the CLI catches FileNotFoundError/ValueError into `{success: False}`); the repo's existing gzip-bomb doctrine - `runtime/http_routes.py` `_read_body`/`_bounded_gunzip` + `runtime_ingest_max_body_bytes` ("checked on both the on-wire and decompressed size") and `security.get_max_response_bytes` (the arg-or-config cap resolver shape, #425); `SECURITY.md`; `tests/test_scip_evidence.py` (25), `tests/test_v1_108_95.py` (pins `_bounded_gunzip` by name). No prior `.colibri_reviews` record.

## Verdict
A SCIP index is a build artifact the operator did not write, and the reader materialised it whole - twice, if gzipped - with no bound, while the sibling runtime ingest path already carried a two-sided cap. Fixed by reusing that guard.

## Bugs & vulnerabilities
**[HIGH] Unbounded `read_bytes()` + `gzip.decompress()` of the `import-scip` input — CONFIRMED — FIXED** - `line 273-275`
- What: a `.scip.gz` of a few KB (64 MiB of zeros gzips to ~64 KB) forced the process to allocate the full decompressed blob before any "is this SCIP-shaped" check ran; nothing on the path bounded it (`max_rows` caps sqlite rows written AFTER parsing). Trigger: `jcodemunch-mcp import-scip bomb.scip.gz` - operator-supplied, but the operator does not author the artifact, and the repo already treats the equivalent runtime payloads as untrusted.
- Fix: `parse_scip_file(path, max_bytes=None)` caps the input twice - on the file's on-disk size before reading, and on the decompressed size through `security.bounded_gunzip` (at most cap + 1 output bytes ever exist). The cap resolves like every other cap in `security.py`: explicit arg > `scip_import_max_bytes` / `JCODEMUNCH_SCIP_IMPORT_MAX_BYTES` > default 256 MiB (a stated bound clearing every real index seen; scip-typescript on a large monorepo runs to tens of MB); a literal 0 opts out; a typo in config falls back to the default, never to uncapped. Over the cap raises ValueError naming the size, the limit and the knob - the CLI already turns ValueError into `{success: False}`. A corrupt gzip stream is now also a ValueError (it was an unhandled `OSError`/`EOFError` out of `gzip.decompress` before).

## Refuted (recorded so they are not re-raised)
- `ScipDocument.relative_path` path traversal: it is only ever a dict key / SQL argument to `resolve_to_symbol_id`, never opened on disk.
- The hand-rolled varint/field walker can hang: `_read_varint` is capped at 10 bytes and bounded by the buffer every step; `_iter_fields` rejects an oversized declared length before slicing; nesting is fixed and shallow.
- Malformed protobuf crashes the caller: `parse_scip_bytes` re-raises everything as ValueError; the CLI catches it.

## Adversarial verification (Phase 3)
- The bomb test measures with `tracemalloc` that the peak allocation while refusing a 64 MiB bomb at a 1 MiB cap stays under 4 × cap - the guard is proven by memory, not by the error message alone.
- The on-disk check is exercised with a plain 8 KiB file at a 4 KiB cap; the config path with `_GLOBAL_CONFIG` monkeypatching (the `test_response_cap.py` pattern); the opt-out (0) and the typo fallback are pinned.
- Controls: a real (minimal, hand-encoded) gzipped index parses under the cap and with the cap disabled; `runtime.http_routes._bounded_gunzip` is the same object as `security.bounded_gunzip`; `tests/test_scip_evidence.py` and `tests/test_v1_108_95.py` unchanged.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `8be25d9f5bcef6e9c6da6d90077eb1b1bc2fe1ed8c53c9f5b19526bc29e73914`. TDD: `tests/test_scip_import_cap_reaudit.py` (7 tests; the battery imports the new names, so it is RED by ImportError on the old bytes - the audit probe `probe_jcm_evidence_scip_1.py` is the behavioural reproducer: 4/5 FAIL before; after, its two behavioural checks PASS with the cap set below its 64 MiB bomb (`JCODEMUNCH_SCIP_IMPORT_MAX_BYTES=33554432` - under the 256 MiB default the bomb is simply under the cap and is materialised, bounded), and its two remaining checks look for a `SIZE`/`MAX_BYTES` substring in `dir()` of each module, a naming heuristic the knob (`get_max_scip_import_bytes` + a config key + a parameter) does not satisfy by construction - recorded, not gamed). Supporting edits in the same commit: `security.py` gains `DEFAULT_MAX_SCIP_IMPORT_BYTES` / `get_max_scip_import_bytes` (the `get_max_response_bytes` shape) and `bounded_gunzip` (moved verbatim from `runtime/http_routes.py`, which now imports it and rebinds the old name at module level - `_bounded_gunzip = bounded_gunzip` - so `tests/test_v1_108_95.py` still reaches it; the gate's pre-review removed-symbol check refused round 1 because it does not count an `import … as` alias as a binding - EV-077, the assignment form is the fix); `config.py` gains `scip_import_max_bytes` at its four sites (env map, defaults, types, the JSONC template comment).
