# Colibri review — src/jcodemunch_mcp/tier_resolver.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tier_resolver.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `c8b72334a3104aa13e617078baf7e3380a15c5e1ec2501e8c635901e27c3fb41` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `normalize_model_id` 16-30 (lower-case, strip a provider prefix up to the last `/`, a trailing `[...]` suffix and a `-YYYYMMDD` date), `resolve_model_to_tier` 33-93 (layers: exact on normalised keys; glob against `key.lower()` RAW at 73; substring with `max(len(raw key))` at 85; wildcard; fallback) and its docstring's "longest-matching key wins so a more specific entry beats a broader one"; this module IS the Model-Driven Tool Tiering mechanism the session's own operating instructions describe - a wrong tier changes which tools a model sees; `tests/test_tier_resolver.py` + `test_tier_runtime.py` (58); the audit probe re-run on these bytes (2/4 FAIL). No prior `.colibri_reviews` record.

## Verdict
Two of the five matching layers compared in a different space from the id they were matching. Both confirmed and fixed; the sub-agent's two self-refutations re-checked and kept.

## Bugs & vulnerabilities
**[MEDIUM] glob keys were matched raw, so a provider-prefixed glob never matched — CONFIRMED — FIXED** - `line 72-74`
- What: the incoming id is normalised (`anthropic/claude-haiku-4-5` -> `claude-haiku-4-5`) but a glob key was only lower-cased, so `anthropic/claude-*` could never match and the id fell through to the wildcard/`full` fallback - a config author writing keys in the same provider-prefixed form the literal layer accepts got the wrong tier silently.
- Fix: `_glob_pattern(key)` - lower-case and strip the provider prefix, like `normalize_model_id`, but deliberately WITHOUT the bracket/date stripping: `normalize_model_id` on a glob would eat a trailing character class (`gpt-4[o]`). Pinned both ways (the prefixed glob matches; a trailing `[o]` class still works and still rejects `gpt-4x`). The sub-agent's snippet (`normalize_model_id(key)`) would have introduced exactly that regression.

**[MEDIUM] substring specificity measured the raw key, not the normalised match — CONFIRMED — FIXED** - `line 79-86`
- What: `max(len(raw key))` - a key decorated with a long provider prefix (`vendor-prefix-that-is-really-long/claude`, normalising to the broad `claude`) out-ranked a bare, more specific `claude-3-opus`, inverting the documented rule.
- Fix: the hit carries its normalised form and the tie-break measures that; two bare keys still resolve to the more specific one in either insertion order (pinned).

## Refuted (sub-agent's own, re-checked and agreed)
- `_DATE_SUFFIX_RE` stripping a legitimate 8-digit suffix: applied symmetrically to id and keys, so a false strip cannot by itself change the resolved tier.
- Exact-match winning over a more specific glob/substring: the docstring defines exact as the top layer by design.

## Adversarial verification (Phase 3)
- Provider-prefixed globs in three spellings (plain, upper-cased, double prefix) match with the `glob:` reason naming the raw key; a bare glob still matches.
- The character-class guard fails on the sub-agent's snippet and passes on this fix.
- The normalised-length tie-break is asserted with the fixture invariant (`len(raw a) > len(raw b)` and `len(norm b) > len(norm a)`) checked in the test itself.
- `tests/test_tier_resolver.py` + `test_tier_runtime.py` (58) unchanged: 65 passed with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `cdd285631ed20252d7b088773ba3ad1a2d2d47041e8d9cefcff2fc04c5c7b06d`. TDD: `tests/test_tier_resolver_reaudit.py` (7 tests) - 5 RED on the old bytes, 2 controls green throughout, GREEN after; the audit probe ALL PASS.
