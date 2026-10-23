# Colibri review — src/jcodemunch_mcp/org/store.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\org\store.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `1b79c1e24a4a526aa6631b366d52c1bc441817847d144b6b9c60d03108f13bb8` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: reviewed as the home of the fix for the org/http_routes.py finding (the sub-agent's org/store review pointed at that finding rather than counting it twice); `record_seat_report` 48-76, `org_rollup`, `_connect` (schema: `usd REAL`, `tokens_saved`/`calls INTEGER`, primary key `(org_id, seat_id, date)`); callers `org/http_routes.py` and `org/report.py`; `tests/test_org_rollup.py`. No prior `.colibri_reviews` record.

## Verdict
The store accepted any number and any string for `date` from either of its two writers; it now owns the one validation rule both share.

## Bugs & vulnerabilities
**[HIGH, shared with org/http_routes.py] `record_seat_report` stored non-finite, negative and bool values and any `date` string — CONFIRMED — FIXED** - `line 59-61`
- Fix: `validate_seat_report(tokens_saved, usd, calls, date) -> str` - refuses bools and non-numbers, non-finite and negative values, and a `date` that is not an ISO calendar day (empty = today, as before); returns the date to store. `record_seat_report` calls it after the id check; a ValueError is what the HTTP route already turns into 400 and what the local report path already surfaces.

## Adversarial verification (Phase 3)
- Pinned directly and through the HTTP route (see the http_routes record); `tests/test_org_rollup.py` unchanged and green.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `ba686eee9ec1bebb600d54c7a0a78c74ce430ea1adf0d7c851a172c1d35c06b0`. TDD: `tests/test_org_report_validation_reaudit.py` (14 tests) - 12 RED on the old bytes (six non-finite/negative values through the endpoint, JSON bools, four malformed dates, the store's own rule), 2 controls green throughout (an empty date means today; an honest report - and an all-zero one - still records and rolls up), GREEN after. The audit probe passes after.
