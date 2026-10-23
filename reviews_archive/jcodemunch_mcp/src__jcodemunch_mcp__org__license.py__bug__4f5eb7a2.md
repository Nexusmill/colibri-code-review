# Colibri review — src/jcodemunch_mcp/org/license.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\org\license.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `4f5eb7a292f648c54b695c48cb35c6adad02374e406ddd5c3b8038656b27e352` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted, 1 PLAUSIBLE documented-as-intentional); `_check_server._parse` 127-134 (the only shape check is `isinstance(valid, bool)`; `tier`/`error` pass through untyped), `check_gate` 289 (`(res.get("tier") or "").lower()`), the cached state file (`_save_state`, plaintext, predates any shape check); the gate's own contract: fail closed on a server that cannot be trusted, never crash. No prior `.colibri_reviews` record.

## Verdict
The body is trusted over the status code, so its shape cannot be: a numeric `tier` walked straight into `.lower()` and the gate raised instead of failing closed. Fixed at the parse and at the consumer.

## Bugs & vulnerabilities
**[MEDIUM] `check_gate` crashed with AttributeError on a non-string `tier` (or `error`) from the license server — CONFIRMED — FIXED** - `line 132-134, 289`
- Trigger (audit probe, RED on these bytes): `_check_server` returning `{{"valid": True, "tier": 5}}` → `AttributeError: 'int' object has no attribute 'lower'` out of `check_gate`.
- Fix: `_parse` keeps `tier`/`error` only when they are strings (else None); `check_gate` lowers the tier only if it is a string - the cached state file predates the parse check and could carry an older non-string value.

## Noted, not fixed (from the sub-agent, verified as documented behaviour)
- Sticky-offline caching has no maximum staleness bound (the module docstring names it as intentional); `_save_state` persists the unmasked key in plaintext at `<CODE_INDEX_PATH>/license.json` - a missing safeguard for the owner, not a defect in this finding's scope.

## Refuted (recorded so they are not re-raised)
- Grace-clock reset by cycling keys; `mask_key` over-revealing 9-12 character keys: both re-traced and stand refuted.

## Adversarial verification (Phase 3)
- Pinned through `check_gate` with `_check_server` monkeypatched: int, float, bool, list and dict tiers all yield a dict with `allowed` and never `mode == "licensed"`; a non-string `error` is dropped; control: a real string org tier still licenses.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `688c006129dde406f9f7511ac7c869726ace575e6fc8c954685c204531589d32`. TDD: `tests/test_tail_batch1_reaudit.py` (16 tests across the three units of this batch) - 13 RED on the old bytes, 3 controls green throughout, GREEN after; the audit probe passes after.
