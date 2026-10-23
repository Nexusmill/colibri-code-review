# Colibri review — src/jcodemunch_mcp/parser/context/base.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\parser\context\base.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `32475b2c8cd1b73308af1dccc5c85fcc3c4c3ebd702c604cdced087fb483ce97` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted); `enrich_symbols` 318-351 (`sym.ecosystem_context = "; ".join(context_parts)` - assignment, not append); the writer it clobbered, `template_shared.py::extract_jinja_directives` (`ecosystem_context=f"{language}-template"` on macro/block symbols); the consumer, `summarizer/batch_summarize.py` (the field feeds the AI prompt); `context/git_blame.py` (detects whenever `.git` exists and always returns a properties-only context - so the clobber fired in nearly every repo). No prior `.colibri_reviews` record.

## Verdict
The parser said "this symbol is a template macro"; the first provider with anything to say replaced it, and git blame always has something to say. Fixed: providers add to the parser's context.

## Bugs & vulnerabilities
**[MEDIUM] `enrich_symbols` overwrote a parser-set `ecosystem_context` — CONFIRMED — FIXED** - `line 350-351`
- Trigger (audit probe, RED on these bytes): a `jinja-template` symbol after enrichment reads `git_blame: Properties: last_author (…)` - the template tag is gone.
- Fix: an existing `ecosystem_context` seeds `context_parts` before the providers are consulted; the join is unchanged, so a symbol with no parser context reads exactly as before (control).

## Refuted (recorded so they are not re-raised)
- `_run_with_budget`'s abandoned thread mutating state; per-provider `existing = set(...)` recomputation cost: both re-traced and stand refuted.

## Adversarial verification (Phase 3)
- Pinned on a real `Symbol` with a fake provider matching the real `get_file_context(file_path)` / `summary_context` / `search_keywords` protocol: the tag survives and the provider's text and keywords are appended; control: no parser context → the provider's text alone.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `c1a4f43885ab36c682f3a3a456c250837f73c08e10b2432308a2462b43acb00f`. TDD: `tests/test_tail_batch2_reaudit.py` (7 tests across the four units of this batch) - 4 RED on the old bytes, 3 controls green throughout, GREEN after; the audit probe passes after.
