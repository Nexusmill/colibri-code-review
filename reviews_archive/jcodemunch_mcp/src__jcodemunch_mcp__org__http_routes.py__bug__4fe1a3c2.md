# Colibri review — src/jcodemunch_mcp/org/http_routes.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\org\http_routes.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `4fe1a3c2114231e76979a86727647f5a4dabd21e8b3e5f4a301275bc7b198f62` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 2 refuted); `handle_org_report` 43-84 (`int()`/`float()` coercion at 67-72 and nothing else; `date` passed through at 73); `org/store.py::record_seat_report` 48-76 (no validation, `INSERT … ON CONFLICT` keyed by `(org_id, seat_id, date)`) and `org_rollup` (sums every seat); the second writer `org/report.py` (a seat's own local report - same store, same aggregate); `tests/test_org_http.py` (the Starlette TestClient + `_GLOBAL_CONFIG` fixture shape), `tests/test_org_rollup.py`, `tests/test_v1_108_73.py`. The two refuted claims (auth bypass; unlicensed read) were re-traced and stand. No prior `.colibri_reviews` record.

## Verdict
The paid org dashboard summed whatever any seat holding the shared ingest token posted: Python's `json` accepts `Infinity`/`NaN` literals, so one report of `usd: Infinity` made every seat's total read `inf` for good, and negatives subtracted. Fixed where every writer meets the store.

## Bugs & vulnerabilities
**[HIGH] Unvalidated `tokens_saved`/`usd`/`calls` (Infinity, NaN, negatives, bools) and an arbitrary `date` string poisoned the org aggregate — CONFIRMED — FIXED** - `line 67-73`
- What: `float("inf")` and `float("nan")` are what `json.loads` hands over for the `Infinity`/`NaN` literals; `int(True)` is 1; `-5` is a fine int. `record_seat_report` stored them and `org_rollup` summed them. Trigger (audit probe, RED on these bytes): an honest seat at 7.5 USD, then `{{"seat_id": "attacker", "usd": Infinity}}` → HTTP 200 → the org total is `inf`.
- Fix: the rule lives in `org/store.py::validate_seat_report` (finite, non-negative, not a bool; `date` empty = today, else an ISO calendar day that round-trips) and `record_seat_report` applies it, so the HTTP route AND the seat's local report path share it; the store's ValueError already landed as this route's 400. The route additionally refuses JSON bools before coercion (`int(True)` would have laundered them) and catches `OverflowError` (`int(float("inf"))`), which used to escape as a 500.

## Refuted (recorded so they are not re-raised)
- Org routes bypass the bearer-auth middleware: mounted in the same app + middleware list as every route; `_ingest_auth_error()` checks the same token the middleware gates on.
- Rollup data readable over HTTP without the license gate: only `POST /org/report` is registered; reading is CLI-only behind `check_gate()`.

## Adversarial verification (Phase 3)
- Pinned through the real Starlette route (TestClient, `CODE_INDEX_PATH` isolated): each rejected value gets a 400 AND the rollup afterwards still shows exactly the honest seat at 7.5 - refusal is proven by the aggregate, not by the status code alone.
- The store rule is pinned directly (`record_seat_report` raises for inf, a negative count and a bad date, and records nothing).
- Controls: an honest report and an all-zero report record and roll up; an empty date still means today.
- `tests/test_org_http.py`, `tests/test_org_rollup.py`, `tests/test_v1_108_73.py` unchanged and green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `33060a3a2ced021cde17b53f4253f51523ddd516739d808bff15e8ae1bdbb45d`. TDD: `tests/test_org_report_validation_reaudit.py` (14 tests) - 12 RED on the old bytes (six non-finite/negative values through the endpoint, JSON bools, four malformed dates, the store's own rule), 2 controls green throughout (an empty date means today; an honest report - and an all-zero one - still records and rolls up), GREEN after. The audit probe passes after.
