# Colibri review — src/jcodemunch_mcp/retrieval/verdict.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\retrieval\verdict.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `dc5d9ab5a4c1e05aae6f2b86c88b1b5728f6414bc4a6f31e31a9db8c7176ded9` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 3 refuted, and its own late correction that the `index_changed` behaviour was pinned as deliberate); `build_verdict` 187-434: the ten STATE_DEGRADED gates for a zero-result scan (236-312: timed_out, semantic requested but unavailable, index_changed, coverage incomplete, working-tree blocks, freshness unknown, moved during scan, incomplete inputs, packed empty, absence unprovable) and the legacy block 422-434 (`_packed_empty` re-deriving SIX of them by hand); the five top-level sinks of `negative_evidence` (`tools/search_symbols.py` ×3, `tools/get_ranked_context.py` ×2 - rendered as "Do not claim this feature exists"); `config.py` `meta_fields` default `[]` (the correcting `_meta.verdict` is stripped on a default install while the top-level claim survives); AGENTS.md's instruction to treat `no_implementation_found` as authoritative; the v1.108.168 pin `tests/test_v1_108_168.py::test_legacy_negative_evidence_still_fires_mid_rebuild` and the v1.108.184 rule in the code's own comment; 16 importing test files (384 tests) plus the wider v1_108/search/ranked sweep (1,929). No prior `.colibri_reviews` record.

## Verdict
One response could say two things about absence: `_meta.verdict.state = "degraded"` (refused) and a top-level `negative_evidence.verdict = "no_implementation_found"` (claimed) - and the default install deletes the first. Four of the ten degraded gates were left out of the hand-rolled suppression. The suppression now follows the state, which closes the class.

## Bugs & vulnerabilities
**[HIGH] The legacy `no_implementation_found` claim fired for four degraded zero-result gates — CONFIRMED — FIXED** - `line 422-434`
- What: `_packed_empty` listed packed-empty, incomplete, moved, freshness-unknown, working-tree-blocks and absence-unprovable, so a scan that TIMED OUT, ran with its semantic provider UNAVAILABLE, read a corpus PROVEN INCOMPLETE, or was REBUILT underneath still produced `negative_evidence = {"verdict": "no_implementation_found", …}` beside `state: degraded`. Because `meta_fields` defaults to `[]`, a default-configured agent saw only the claim - and AGENTS.md tells it not to re-search. Trigger (audit probe, RED on these bytes): `build_verdict(result_count=0, timed_out=True)` and the coverage/semantic variants.
- Fix: `if result_count == 0 and state == STATE_DEGRADED:` - the carve-out is the state itself, so a gate added later cannot be left out again; the docstring's "fires on exactly the historical trigger" claim (already untrue since v1.108.184) now states the carve-out. Everything else in the legacy block (keys, verdict names, `low_confidence_matches`) is unchanged.
- **Contract flip, stated:** v1.108.168 pinned the rebuild gate's legacy claim as deliberate ("the zero-result trigger is unchanged; only the verdict state moved"). v1.108.184 then made the rule that a scan which cannot establish absence must not say "no implementation found" (the code's own comment), and applied it to six gates; the rebuild gate was the last exception and is closed under that rule. `tests/test_v1_108_168.py::test_legacy_negative_evidence_still_fires_mid_rebuild` is renamed `…stays_silent_mid_rebuild` and asserts `negative_evidence is None`, `state == "degraded"`, `absence_refused is True` - the same commit, called out in its message.

## Refuted (recorded so they are not re-raised)
- if/elif ordering lets a later gate produce a false STATE_ABSENT: every degraded gate precedes the bare `result_count == 0 → absent` fallback.
- `_semantic_provider_available()` can crash `build_verdict`: wrapped, fails toward "unavailable".
- `index_channel` lets fresh-but-incomplete read as current: `coverage_is_incomplete` is checked before the stale/freshness branches.

## Observation (PLAUSIBLE, not fixed)
- There is no STATE_DEGRADED gate for `index_stale` with zero results - a stale index cannot prove absence any more than a rebuilding one - although the 168 comment speaks of "the stale and truncated gates". Whether `handoff.absence_refusal` refuses on `channels.index == "stale"` was not traced here; recorded for the retrieval owner, out of this finding's scope.

## Adversarial verification (Phase 3)
- Pinned directly on `build_verdict`: the four omitted gates (semantic unavailability via monkeypatched `_semantic_provider_available`) each yield `state == degraded` AND `negative_evidence is None`; an invariant test walks all ten gates and asserts state, silence and `absence_refused` together.
- Controls: a clean zero result still says `no_implementation_found` with its counts; `low_confidence_matches` and hits are unchanged; a rebuild WITH results still returns them and discloses `channels.index == "rebuilding"`.
- 178 tests in the nine closest files and 1,929 in the wider verdict/search/ranked/absence/v1_108 sweep green with the battery; the probe passes.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `e2c3226bcec3a4a5cb37ac4cb07c71409d5ac72ebdc6e135ec52723c720f10ce`. TDD: `tests/test_verdict_negative_evidence_reaudit.py` (8 tests) - 5 RED on the old bytes, 3 controls green throughout, GREEN after; one existing pin flipped as stated above.
