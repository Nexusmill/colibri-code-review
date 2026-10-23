# Colibri review — src/jcodemunch_mcp/evidence/receipts.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\evidence\receipts.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `01a97f10a8ef4e765969c53f644b7d9238be66c93a3f8195b6f48a2637eea3a0` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's PARTIAL review (a PLAUSIBLE, unprobed finding; 1 refuted) - verified here by construction; `_canonical` 108-110 (`default=str`), `record_receipt` 224-265 (stores the raw `envelope` object beside the canonical payload), `lookup` 290-310 (`json.loads(json.dumps(rec["envelope"]))` - no `default`), `envelope_json` 323-329 (same); the producers (`evidence/producers.py`, reviewed today) build envelopes from tool outputs. No prior `.colibri_reviews` record.

## Verdict
The id and the collision check rendered a non-JSON-native value with `default=str`; every read path did not. Such a receipt could be minted but never cited. Verified by construction and fixed at the one write.

## Bugs & vulnerabilities
**[LOW-MEDIUM] A receipt carrying a non-JSON-native value stored fine and raised TypeError on every read — CONFIRMED by construction (was PLAUSIBLE) — FIXED** - `line 254, 307, 329`
- Trigger: an envelope with a `pathlib.Path` (or a set, a datetime) in it → `record_receipt` returns the id, `lookup` raises `TypeError: Object of type WindowsPath is not JSON serializable`. Whether a producer emits such a value today was not established (PLAUSIBLE in the wild); the module's own contract ("a proof that renders differently on the second read is not a proof") is what the fix protects.
- Fix: `record_receipt` stores `json.loads(json.dumps(envelope, default=str))` - the JSON-native form, normalised once - so `lookup` and `envelope_json` always succeed and every read sees what the id was computed over; an envelope that cannot be rendered even with `default=str` is refused (None) rather than stored unreadable.

## Refuted (recorded so it is not re-raised)
- The collision check comparing the whole envelope rather than the identity payload: re-traced and stands refuted.

## Adversarial verification (Phase 3)
- Pinned directly: a `Path` and a set in the envelope → recorded, `lookup` returns the normalised envelope, `envelope_json` renders; the module stores are cleaned around the test.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `142f52653ff8577a6a2ed54528da5fc15df4860a21ead616bc782283a8e987ef`. TDD: `tests/test_tail_batch3_reaudit.py` (6 tests across the four units of this batch) - all 6 RED on the old bytes (each for its own reason, verified by the per-test failure), GREEN after; the audit probe passes after where one existed.
