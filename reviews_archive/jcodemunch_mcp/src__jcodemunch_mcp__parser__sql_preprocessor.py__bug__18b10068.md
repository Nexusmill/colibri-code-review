# Colibri review — src/jcodemunch_mcp/parser/sql_preprocessor.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\parser\sql_preprocessor.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `18b10068e44f64b2fca61ca2a8c8cb873bfd8bdaee7b8ee22ba74f94ee948708` (current bytes at dispatch, 2026-09-13; the 2026-09-11 audit summary recorded only the first 12 hex chars; the full digest was reconstructed from the git HEAD blob with the file's CRLF newlines and verified against that prefix)
- date: 2026-09-13
- mode: bug
- context pack: whole file read (187 lines); `find_references` for `strip_jinja` / `extract_dbt_directives` / `JINJA_PATTERN` (consumers: `parser/extractor.py::_parse_sql_symbols`, `parser/template_shared.py::extract_jinja_directives` with `("macro","block")`, `tests/test_sql_language.py` which only asserts that `__jinja__` appears and the braces are gone); `_parse_sql_symbols` read in full for how the directive offsets and the stripped bytes are consumed; the two audit probes for this unit plus `probe_jcm_extractor_5.py` (the extractor-side symptom of this file's `strip_jinja`) re-run against these bytes, all RED. No prior `.colibri_reviews` record.

## Verdict
Three real defects, all about the same thing — offsets this module hands to the extractor did not address the real file. Fixed in the commit carrying this record; consumers' call shapes unchanged.

## Bugs & vulnerabilities
**[HIGH] `extract_dbt_directives` reports CHARACTER offsets as `byte_offset`/`byte_length` — CONFIRMED — FIXED** - `line 90, 116-117` (pre-fix numbering)
- What: the directive regex runs over `sql_bytes.decode()`; `m.start()` is a str index, stored verbatim as the byte offset the extractor hashes and `get_symbol_content` seeks. One multi-byte character in an earlier comment (probe 2: an `é`) shifts every later directive — 58 reported vs 60 real.
- Fix: new `parser/text_offsets.py::CharToByte`, an incremental char-index → UTF-8-byte-offset cursor (amortised O(n) over the increasing match order); both ends of every directive are converted before the `DbtDirective` is built. The helper is shared with the extractor's regex-based template parsers (Blade/AL/EJS/Razor/Astro), which carry the same defect and get the same fix in their own tranche.

**[MEDIUM] End-tag search is not nesting-aware; an unclosed directive annexes its neighbour — CONFIRMED — FIXED** - `line 93-104` (pre-fix numbering)
- What: a bare `search()` for the first `{% endmacro %}` after `m.end()` let an unclosed `{% macro foo %}` swallow the following macro's body and end tag (probe 1: foo's span ran through bar's `endmacro`).
- Fix: `_find_block_end` scans start/end tags of the same keyword with a depth counter and returns the end tag that brings depth to zero, or `None` (the directive then ends at its own opening tag, as before). Nested same-keyword blocks close at their own tag (`test_nested_same_keyword_directive_closes_at_its_own_end_tag`).

**[MEDIUM] `strip_jinja` shrinks the file, so every tree-sitter SQL symbol after the first Jinja token carries offsets and a content hash into text that is not in the file — CONFIRMED (reported against the extractor unit, fix point is here) — FIXED**
- What: `JINJA_PATTERN.sub("__jinja__", …)` replaced spans of any length with nine bytes; `_parse_sql_symbols` then parsed the shortened bytes and stored `node.start_byte` as if it addressed the file (probe 5: `CREATE TABLE` reported at 115, real 215; slice returned `o\n{% macro f`).
- Fix: `strip_jinja` now works on the BYTES tree-sitter will parse, replacing each span with a placeholder of the same byte length (`__jinja__` padded with spaces; spans shorter than nine bytes become underscores, still an identifier) and keeping every newline where it was — so byte offsets AND line numbers survive. `_parse_sql_symbols` additionally hashes the REAL bytes at those offsets (a symbol whose span contains a Jinja token would otherwise hash the placeholder; `test_symbol_spanning_a_jinja_token_hashes_the_real_bytes`). The existing `test_sql_language.py` expectations (`__jinja__` present, braces gone) still hold.

## Refuted (sub-agent's own, re-checked and agreed)
- ReDoS in `JINJA_PATTERN` / `_directive_pattern` / `_JINJA_COMMENT_RE` — every quantifier is a single-level lazy one with no nested repetition.
- Runaway `_extract_preceding_docstring` scan — bounded by the contiguous comment block, breaks on the first other line.

## Adversarial verification (Phase 3)
- `CharToByte` cross-checked against `len(text[:i].encode())` for every index of a mixed 1/2/3/4-byte string, including the restart path.
- The length-preserving strip was verified byte-for-byte outside the Jinja spans and newline-position-for-newline-position across four shapes (multi-line comment, tiny `{{x}}`, non-ASCII inside the span, the dbt `config()` header).
- Checked `template_shared.extract_jinja_directives` (the other consumer) still receives the same `DbtDirective` shape — only the values became correct.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `ece0cd03a65ec788b771b15f93d8bebfd62e90ba59c5e0fd7ee4f575e1e24f72`; new module `parser/text_offsets.py`. TDD: `tests/test_sql_preprocessor_offsets.py` (10 tests) — the offset, nesting, and hash tests RED on the old bytes, GREEN after; `tests/test_sql_language.py` unchanged; probes sql_preprocessor 1+2 and extractor 5 ALL PASS.
