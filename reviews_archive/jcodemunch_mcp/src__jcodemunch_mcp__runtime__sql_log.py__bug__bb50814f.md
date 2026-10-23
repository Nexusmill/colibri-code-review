# Colibri review — src/jcodemunch_mcp/runtime/sql_log.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\runtime\sql_log.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `bb50814f99f9f43c1ab42a0237b0701506bbb7b3df34097d5729ba1037309b03` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline; lines 258-406 read in full (all six regexes + `_build_record`/`_extract_tables`/`_extract_columns`); `search_text` for `_SELECT_LIST_RE` (single use, line 371 — no other reference in src or tests) and `requires-python` (>=3.10, so possessive quantifiers/atomic groups are NOT available and a regex-only fix cannot be made linear); callers `_parse_pg_stat_statements_csv`/`_parse_json_lines`/`_record_from_json_obj` → `_build_record`, plus `runtime/sql_ingest.py` calling `_build_record` a second time per row under redaction; the audit probe re-run on these bytes (RED, 2.97 s for 644 KB); the pre-fix outputs of `_extract_tables`/`_extract_columns` on eight representative queries captured to lock semantics.

## Verdict
Not shippable before this tranche: a single whitespace-heavy SQL row could pin a worker for seconds-to-hours on the file-import and `/runtime/sql` live-ingest paths. Fixed (linear) in the commit carrying this record, together with a phantom-column defect found while locking the extractor's semantics.

## Bugs & vulnerabilities
**[HIGH] `_SELECT_LIST_RE` backtracks polynomially on whitespace-heavy SQL (CPU DoS on untrusted log content) — CONFIRMED — FIXED** - `line 270, 371` (pre-fix numbering)
- What: `(?is)\bSELECT\b\s+(?:DISTINCT\s+)?(?P<list>.+?)\s+\bFROM\b` — the lazy `.+?` and the separately quantified `\s+` before `FROM` are two owners for every whitespace run; for each of the O(n) extension points of `.+?` inside a run of length w the engine retries `\s+` up to w ways, giving O(w²) per run and ~O(n³) overall. Measured on the audit probe's shape (`"col" + n spaces + "( "`, repeated n times, then ` FROM t`): 2.97 s at n=800 (644 KB) on these bytes.
- Trigger: any ingested query row with many whitespace-padded tokens — formatter-mangled SQL is enough; a crafted row inside the default HTTP body cap does it deliberately. Runs once per row (`_build_record` → `_extract_columns`), twice with redaction on (`sql_ingest.py`).
- Impact: worker CPU exhaustion from a single record.
- Fix: replaced the one-pattern extraction with `_select_list()` — two anchored keyword searches (`\bSELECT\b`, then `\bFROM\b` from `sel.end()`), slice, drop a leading `DISTINCT`, strip. Linear by construction (each search is a plain scan). Post-fix: 0.03 s at 644 KB, 0.11 s at 2.5 MB, 0.43 s at 10 MB (≈4× time per 4× input).
- Why not the sub-agent's regex-only snippet (drop the `\s+` before `FROM`): it removes the O(w²) term but leaves the leading `\s+` after `SELECT` with O(k) backtracking positions on a failing match, still super-linear on a `SELECT` followed by a long whitespace run with no `FROM`; and `requires-python >= 3.10` rules out possessive quantifiers. The searches are simpler and provably linear.
- Semantics preserved (locked by `test_extraction_semantics_locked`, expectations captured from the OLD bytes): first `SELECT`, first `FROM` after it, whitespace required right after `SELECT` (`SELECTFROM t` still yields nothing), `DISTINCT` dropped, result stripped. The one deliberate difference: `FROM` no longer needs whitespace before it (`SELECT (a)FROM t` now extracts `a` where the old pattern extracted nothing) — strictly more correct.

**[MEDIUM] `_BARE_IDENT_RE` backtracks an identifier to a shorter prefix to satisfy its call-paren lookahead — NEW, CONFIRMED — FIXED** - `line 283` (pre-fix numbering)
- What: `(?<![A-Za-z_."])IDENT(?!\s*\()` — when `count(` fails the lookahead, the greedy `[A-Za-z0-9_]*` inside IDENT gives back one char and `coun` (not followed by `(`) matches. Every function call in a SELECT list or predicate therefore produced a phantom column: `count(*)` → `('', 'coun')`, `max(price)` → `('', 'ma')`.
- Impact: bogus `runtime_columns` rows / mis-attributed column confidence on every aggregate query. Found by reading the captured pre-fix outputs (the sub-agent did not report it).
- Fix: `(?![A-Za-z0-9_]|\s*\()` — the identifier must end at a word boundary before the paren test is judged. `test_function_names_are_not_columns` pins `count(*), max(price), lower (name)` → `[('', 'price'), ('', 'name')]` (the arguments are real column refs; the function names are not).

**[LOW] No per-record cap on `sql` length before extraction — CONFIRMED as stated, NOT FIXED** - `line 302`
- Defence-in-depth only (the sub-agent's own framing). With extraction linear and the HTTP path already bounded by `runtime_ingest_max_body_bytes`, a cap would be policy, not a fix; left open.

## Refuted (sub-agent's own, re-checked)
- `_TABLE_RE`'s `(?:IDENT\.)*IDENT` as an independent blowup — refuted by measurement (0.035 s for a 200k-repetition chain); each `IDENT.` repetition is delimited by the literal dot, so there is no ambiguity to backtrack over. Agreed on reading.

## Adversarial verification (Phase 3)
- Re-derived the O(n³) mechanism from the pattern rather than trusting the probe's number, then confirmed the probe RED on the exact bytes and ALL PASS after.
- Checked `_PREDICATE_BLOCK_RE` (`.+?` + alternation lookahead, `finditer`) for the same class: each lazy step tests one lookahead, no second quantified owner of the same characters — linear per block; not a finding.
- Checked that `_select_list` cannot regress the eight locked queries: parametrized test green on old and new bytes except the two rows that carry the phantom-column fix.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `cf1dfac1595245a504c7940845f53c169a1b341acd9184cc606afe194af10017`. TDD: `tests/test_runtime_sql_log_hardening.py` — the timing test (2.97 s → RED at a 1.5 s budget) and the two phantom-column rows RED on the old bytes, GREEN after; sql/runtime suites (329) green.
