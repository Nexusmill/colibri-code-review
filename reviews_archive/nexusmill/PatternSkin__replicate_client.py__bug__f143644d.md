# colibri-review — PatternSkin/replicate_client.py — bug (hunt round 1, effort=mid)

- **Source:** PatternSkin/replicate_client.py · **Scanner:** general-purpose subagent @ claude-sonnet
  (mid) · **Verification + fix:** claude-opus-4-8[1m] (in-session, Phase 3) · cost $0.00
- **sha256 reviewed:** f143644de3bad879035ed85720953279ca3d0cc900d094eccc7e99423980f420
- **Date:** 2026-07-23 · **Mode:** bug · round 1 of the top-20 hunt (mid pass), stale-file DELTA
- **Context pack:** prior review `…__042707a0.md` (K3) + remediation rows 158a10e / glm20-1 (SSRF +
  redirect-token-leak, verified fixed) — SSRF allowlist, no-redirect opener, poll-loop hardening,
  `pred["output"]` guard, unknown-model pricing all confirmed closed. Sole caller: `filmstrip.py`
  (daemon thread, broad `except Exception`). Pure stdlib (no bpy) → headlessly testable.

## Verdict
The security fixes hold, but the create-retry loop had a **HIGH money-safety defect**: a transient
5xx or read-timeout re-POSTed the prediction-create call up to 5×, each a separately-billed
prediction. Fixed with a money-safe retry policy, plus a JSON-contract fix and two LOW hygiene
fixes. One runtime-budget/cancel gap deferred (largely mitigated by the HIGH fix).

## Bugs & vulnerabilities

**[HIGH] Retrying the prediction-CREATE POST on 5xx/timeout double-bills** - `replicate_client.py:119-131`
- What: the create loop retried on `429/500/502/503/504` (and any `URLError`) with no idempotency
  key. The request carries `Prefer: wait` (line 109), which holds the connection while Replicate
  runs the job — so a `504` (or a read-timeout at `timeout=150`) is the classic "server finished,
  client gave up" case, **not** "never reached the server." Re-POSTing creates and bills another
  prediction.
- Impact: one user click → up to 5 billed predictions on a flaky connection. Directly spends the
  user's money (G19).
- Fix: retry only `429` (server rejected *without* creating) and pure connection failures
  (refused/DNS — never reached the server). On `5xx` and read-timeouts, raise with a
  "a prediction may have been created and billed; check replicate.com" message instead of silently
  re-charging.
- **Verified by execution:** pre-fix, a single mocked `504` issued **5 POSTs** and a read-timeout
  issued **5 POSTs**; post-fix each issues exactly **1** and raises the billing warning, while a
  `429` still retries (2 POSTs).

**[MEDIUM] Malformed JSON on a 2xx create escaped as raw `JSONDecodeError`** - `replicate_client.py:117`
- What: `json.loads(r.read())` in the create loop was guarded only by `HTTPError`/`URLError`;
  `JSONDecodeError` (a `ValueError`) slipped out raw, breaking the client's `RuntimeError` contract
  (the poll loop three lines away already catches `ValueError`).
- Fix: `except ValueError → RuntimeError("…unreadable response…")`, no retry (the create was
  processed — retrying would double-bill).
- **Verified:** pre-fix leaked `JSONDecodeError`; post-fix raises `RuntimeError`.

**[LOW] `int(seed)` raised a raw `ValueError`** - `replicate_client.py:107` — wrapped to a clear
`ValueError("invalid seed …")`. Mitigated today (the only caller passes `random.randint(...)`), but
this is a documented vendored client. Verified pre/post.

**[LOW] Retry branch never released the `HTTPError` socket** - `replicate_client.py:120` — `e.close()`
before `continue` in the 429 branch.

## Deferred (RC-1, `docs/deferred_manifest.json`)
- The `timeout` param bounds only the poll loop; the create-retry phase used a hardcoded
  `150s × attempts`. The HIGH fix removes the 5× 5xx/timeout path (the ~15-min worst case), so the
  remaining multi-attempt path is 429/connection-refused with bounded backoff — largely mitigated.
  The full fix (fold create-retry into one `timeout` clock **and** add a `cancel()`/`DELETE` helper
  so a user who abandons a run can release still-billing predictions) is deferred — the cancel
  helper is a feature addition wanting its own design.

## Verify
`junk/_replicate_test.py` — post-fix **11/11 PASS**, pre-fix **5/11** (verified by restoring HEAD
bytes): pre-fix a 504 and a timeout each issued 5 POSTs and JSON/seed leaked raw exceptions;
post-fix single POST + billing warning, RuntimeError, clean ValueError. `_rc_urlopen` monkeypatched
— no network touched. Fixes via `_safe_edit` (G8).

## Refuted during verification (deep scan self-refuted; recorded in `_refuted_ledger.json`)
- CRLF header-injection via a malicious bearer token — `http.client.putheader` raises
  `ValueError` on `\r`/`\n` in a header value before sending; mitigated by the stdlib, not this file.
- `_HTTP_OPENER` lazy-init race between threads — worst case builds two identical no-redirect
  openers; no correctness/security/money impact.
- Poll loop reusing a stale `get_url` / `pred` being `None` after the loop — `get_url` is static per
  prediction id; every loop branch either `break`s with `pred` set or raises.
