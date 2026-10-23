# Colibri review — src/jcodemunch_mcp/parser/extractor.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\parser\extractor.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `359c0eabb6b395f7b9644b71e9b39e3a87d68c3b47dac90a9f8c181f683db247` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline; 10,732 lines)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline; `_walk_tree` (510-640), `_extract_variable_function` (1403-1466), `parse_file`'s dispatch (300-413), the Fortran extractor (5760-5909), the Lua/Luau `_resolve_name` helpers (5192-5212 and its Luau twin), the nine `get_parser` try/except sites (9046-9968), `index_folder.py:2744` (the per-file "Failed to parse" handler), `symbols.py:22` + `hierarchy.py:28` (the `Symbol.parent` contract); the six audit probes re-run against these bytes (all RED); the 20 test files that import the extractor (415 tests) plus `test_languages.py` / `test_luau_language.py` / `test_parser.py` read for the assertions that PIN each behaviour before touching it (the 09-06 lesson). No prior `.colibri_reviews` record.

## Verdict
Six real defects. Four are fixed in the commit carrying this record (tranche A); the two that need a mechanical sweep across five template extractors and the SQL preprocessor are CONFIRMED and scheduled as tranche B (below), not dropped.

## Bugs & vulnerabilities
**[HIGH] Deep nesting overflowed the recursive AST walk and index_folder then dropped EVERY symbol of the file — CONFIRMED — FIXED (tranche A)** - `line 510-640` (pre-fix numbering)
- What: tree-sitter builds a left-leaning chain one level deep per operand for `a + a + … + a`; `_walk_tree` recursed once per level, so a generated/minified file with ~1000 terms raised `RecursionError`, `index_folder`'s per-file handler caught it and the whole file went to `warnings` as "Failed to parse" — `def keep_me()` after the chain never made it into the index. Both Python and JavaScript reproduced (probe 2).
- Fix: `_walk_tree` now runs on an explicit stack, children pushed in reverse so the visitation is the identical pre-order (locked by `test_walk_order_is_unchanged_by_the_iterative_walk` and by 1,584 parser/extractor tests unchanged). The ~30 custom-parser `_walk` helpers keep their recursive shape (deep nesting there is a different, rarer scale); recorded as a known residual, not hidden.

**[MEDIUM] JS/TS `const f = () => …` scoped by the parent's bare NAME and always promoted to `method` — CONFIRMED — FIXED (tranche A)** - `line 1424-1428` (pre-fix numbering)
- `A.m.f` and `B.m.f` both became `m.f` (ids collided, `~1/~2` disambiguation), and a closure inside a plain function was a `method`. `_extract_variable_function` now chains through `parent_symbol.qualified_name` and promotes to `method` only under a container (`parent_is_container` passed from the walk) — the same rule `_extract_symbol` already applied (audit V7).

**[MEDIUM] Fortran / Lua / Luau stored a bare NAME in `Symbol.parent` — CONFIRMED — FIXED (tranche A)** - `line 5203, 5209, 5321, 5327, 5783` (pre-fix numbering)
- `symbols.py:22` documents `parent` as a symbol ID and `hierarchy.py:28` attaches children only when `symbol.parent in node_map` (keyed by id), so these members never attached and SQLite stored a bogus parent id. Fortran now stores the module/program's id (`make_symbol_id(filename, name, "class")`, the id `_extract_module_or_program` itself creates); Lua/Luau store `None` because the table (`local M = {}`) is not a symbol — `qualified_name` still carries `M.greet` / `C:speak`.
- **Seven existing tests pinned the defect** (`test_parse_fortran_module_method/_derived_type/_parameter_constant`, `test_luau_module_method/_oop_method`, `test_lua_dot_method/_colon_method` asserted the bare name). They were re-read against the documented contract before deciding which side was wrong; the testers were corrected (G35), not the contract.

**[LOW] Nine custom parsers swallowed a broken grammar as an empty file — CONFIRMED — FIXED (tranche A)** - `line 9046-9968` (pre-fix numbering)
- pascal/matlab/ada/commonlisp/solidity/zig/powershell/apex/ocaml wrapped `get_parser` in `except Exception: return []`; fsharp/clojure/elisp/nim/tcl/dlang did not. The sub-agent's own fix snippet (log a warning, still return `[]`) contradicted its own probe (which asserts propagation); propagation is the right contract — `index_folder.py:2744` turns it into a user-visible "Failed to parse" warning instead of an indistinguishable empty file — so the nine now match the six. Test covers all 12 languages.

**[HIGH] Blade/AL/EJS/Razor/Astro store CHARACTER offsets as `byte_offset` and feed them to a byte-indexed line table — CONFIRMED — FIXED (tranche B, see postscript)** - `_parse_blade_symbols` 2912+, `_parse_al_symbols` 3074+ (14 sites), `_parse_ejs_symbols` 4422+, `_parse_razor_symbols` 4580+, `_parse_astro_symbols` 4880+ (post-tranche-A numbering)
- The regexes run over the decoded `str`; `m.start()` is a char index but `byte_to_line`'s table is built from UTF-8 byte lengths and `get_symbol_content` seeks `byte_offset` in binary. Any non-ASCII text before a match shifts line and slice (probe 1: Astro `byte_offset=115`, expected 215). Same class as #414, which fixed only the tree-sitter extractors. Fix plan: one shared `_utf8_offsets(content)` helper returning `(char_to_byte, byte_to_line)`, applied at every `m.start()`/`match.start()` site in the five functions (each currently carries its own copy of the line table). Deferred to its own tranche because it is ~30 mechanical sites across five functions and deserves its own review, not because it is doubted.

**[MEDIUM] dbt/Jinja SQL symbols carry offsets and content hashes into the Jinja-STRIPPED text — CONFIRMED — FIXED in the `sql_preprocessor.py` tranche (a4214ce; `strip_jinja` preserves the byte layout and `_parse_sql_symbols` hashes the real bytes)**
- `strip_jinja` replaces each `{{ … }}` / `{% … %}` with the 9-byte `__jinja__`, so every tree-sitter offset after the first Jinja token is wrong and never verifies. The fix (length-preserving placeholders) belongs to the `sql_preprocessor.py` unit, which has its own audit summary; cross-referenced there.

## Refuted / not findings
- None of the six was refuted; the sub-agent's severities were kept except that the nine silent-except sites are one LOW, not nine.

## Adversarial verification (Phase 3)
- The iterative walk was validated the hard way: every parser/extractor/language test in the suite (1,584) run before and after — zero behaviour change — plus an explicit pre-order test.
- For the `parent` contract, both sides were read (`symbols.py`, `hierarchy.py`) before overriding the seven pinning tests.
- The probe-vs-snippet contradiction on the grammar sites was resolved by reading the consumer (`index_folder`), not by picking the sub-agent's later word.

## Remediation postscript (tranche A, same commit)
The file is now `21d8a2961a54fb25759d9b0b6762ee116782e2af35d18496e1941cb3c9fbe5f5`. TDD: `tests/test_extractor_reaudit.py` (21 tests) RED on the old bytes for exactly the four fixed findings, GREEN after; probes 2/3/4/6 ALL PASS; seven contract tests corrected. Probes 1 and 5 stay RED by design until tranche B.


## Remediation postscript (tranche B, same-day follow-up commit)
The file is now `5a9bf2400dbba5dee5f4db9748f1e7bed4ab6b1319d6cf40599062386f2afa1f`. The two OPEN items above are closed:
- **Char-vs-byte offsets, all five regex extractors.** Each function now builds a `CharToByte` cursor (`parser/text_offsets.py`, shared with `sql_preprocessor.py`) and every stored position goes through it: Blade (1 site), AL (the object symbol + the 12 child passes; its `byte_to_line` was renamed `char_to_line` and its table built in character units, since the regex positions it receives ARE character indexes), EJS (2), Razor (5 direct sites + both `_rewrap_symbol` callers, with the C# shim's prefix subtracted AFTER the conversion), Astro (3 direct sites + both `_rewrap_symbol` callers, BOM-aware: `content` drops the BOM char while the file keeps its 3 bytes). Line numbers were already char-based in Razor/Astro and are now char-based in Blade/AL/EJS too.
- **Two more anchoring defects found by the new tests, same class, fixed in the same sweep:** Razor's `<script src>` symbol was based at `script_match.start()` (the `<script` tag) while `src_match` positions are relative to the attributes group — off by seven bytes even in pure ASCII — now `start(1)`; EJS's scriptlet functions were based at the `<%` delimiter while `_EJS_FUNC_RE` runs over the inner group — off by two/three — now `start(1)`.
- TDD: `tests/test_extractor_template_offsets.py` (10 tests, incl. the Pass-14 `var` case added after the gate catch: one per extractor with 100 two-byte characters ahead of the symbol, the Razor src anchor, inline-script/`@functions` rewraps, an Astro BOM case, and an ASCII control) — 8 RED on the tranche-A bytes for exactly the drift (offsets 100 short; Razor src 107 short), GREEN after; the 1,322 parser/template tests unchanged; `probe_jcm_extractor_1.py` ALL PASS.
- **Gate round 1 on this tranche (gate_20260913-134623) caught a regression the sweep introduced:** AL's Pass 14 (variable declarations) reads `line_start_offsets[i]` directly and stored it as `byte_offset`; retyping the table to character units silently turned that into a char offset, and no test exercised a `var` section. Confirmed against the bytes, reproduced RED with `test_al_var_section_offsets_after_non_ascii` (a `var` section after 100 two-byte characters), fixed by converting at the store (`to_byte(line_char)`). Side effect worth recording: `_find_parent(line_char)` now compares like with like — under the old byte table it received a byte offset and compared it against the char-unit object ranges. The sweep's own comment claimed every stored position went through `to_byte`; it did for the 13 sites in the site map and not for the one outside it.
- Not changed: the `splitlines()`-based line tables count one newline byte per line, so `\r\n` files still drift one column per line in Blade/AL/EJS — pre-existing, not part of the audited finding, noted here so it is not rediscovered as new.
