<!-- source: src/providers/eachlabs.ts | reviewer: glm-5.3-zai-in-session | sha256: 3a8b7aa8d9f0815c20a66dfb1142c32b60d976ad9a631ccb65465fe8d1ca46fd | date: 2026-09-16 | mode: bug -->
<!-- context: owner commission 2026-09-16: colibri bug hunt on the NEXT top ten files by import PageRank (the board past the hunted ten); fresh-context subagent per file under the 0.3.0 doctrine (prior review = context, never a skip; same-sha files hunt beyond the record). -->

## Verdict

Not clean. The prior review (same sha, 2026-08-27) recorded zero findings — everything here is new ground it did not contain. The poll loop reads only the JSON body and never the poll response's HTTP status, so every terminal poll-level error (401/404/429/5xx/HTML) is indistinguishable from "still running": it silently spins the full 10 minutes and then reports a false "timed out after 10 min" — on the autopilot's paid voice leg, where it also defeats the consumer's message-regex throttle recovery (cross-file break, both sites cited below). The POST leg has a milder sibling: a 60 s response timeout is reported as "unreachable" while the prediction may have been created and billed.

## Bugs & vulnerabilities

**[HIGH] Poll HTTP status is never checked — terminal poll errors spin 10 minutes and misreport as a timeout** — `line 93`-`107`
What: `poll.ok`/`poll.status` are never inspected. Line 94 coerces any non-JSON or JSON-without-`status` body to `{}`; lines 95/100 then see `undefined` status, and line 107 is the only exit — `throw new Error("eachlabs prediction timed out after 10 min")` after the full deadline.
Trigger: prediction ID unknown/expired/purged (404), key revoked or swapped mid-run in SETTINGS (401/403), a persistent 500, or a proxy/HTML error body on a 200. The first poll already knows; the loop ignores it for 600 s.
Impact (traced end to end): (a) film autopilot — `vite.film.ts:1001` `genVoice` awaits this inside the step worker; one narration line stalls the pipeline 10 min per shot (N shots sharing the condition = N × 10 min), then surfaces a false "timed out" — violating the repo's truthful-status doctrine — while the POST already spent real money; the artifact, if one exists, is never fetched. (b) The browser proxy `vite.eachlabs.ts:44` hangs the `/run` fetch 10 min, then 502s with the false timeout message. Reachable today: the EachLabs denylist is per-engine (`autopilot.ts:874` filters `service/slug`), not provider-wide.
Fix: after line 93, branch on `poll && !poll.ok`: 401/403/404 → throw immediately (`eachlabs poll ${poll.status}`); 429/5xx → back off and continue toward the existing deadline. Phase 3: re-opened lines 91-108; no status check exists anywhere in the loop; CONFIRMED (independently re-verified against current bytes by the hunt orchestrator).

**[MEDIUM] Poll-level 429s defeat the consumer's throttle-recovery contract (cross-file break)** — `line 93`-`94` vs `vite.film.ts:1361`/`1391`
What: the autopilot detects throttles by regex on the thrown message — `/429|throttl/i.test(e.message)` (`vite.film.ts:1361`, retry at 1391-1399, 65 s window wait) — and the provider's POST path cooperates by embedding the status (`line 86`: `eachlabs ${created.status}: ...`). The poll path drops the status entirely, so a 429 on `GET /v1/prediction/{id}` never contains "429" in any message.
Trigger: the consumer's own comment documents the account has "6/min slots" (`vite.film.ts:1365`); the fixed 3 s poll cadence (20 req/min per prediction, no backoff) plus parallel keyframe/segment calls through the same key can exhaust them mid-run.
Impact: instead of the designed 65-second wait-and-recover, the step spins 10 minutes, throws "timed out", which does NOT match the regex — the throttle is treated as a hard failure and the shot's voice is lost to the assemble guard. The recovery machinery the consumer built is unreachable for this provider's poll leg.
Fix: include the status in poll-error messages (falls out of the HIGH fix); add backoff/jitter on non-2xx polls so the poller stops provoking the limiter. CONFIRMED (both sites read; the regex cannot match any string this function throws for poll-level 429s).

**[MEDIUM] POST response timeout is reported as "unreachable" while the prediction may exist and bill — retry double-spends** — `line 76`-`82`
What: `AbortSignal.timeout(60_000)` aborts the fetch and `.catch(() => null)` flattens it to `if (!created) throw new Error("eachlabs unreachable")`. An aborted request is not an unreachable server: EachLabs may have accepted, created, and billed the prediction; its ID is lost.
Trigger: POST accepted server-side but response latency > 60 s (queue pressure) or response packet loss.
Impact: the caller is told nothing was reached, retries, and pays twice; the orphaned prediction is never polled or canceled. The message is also untruthful (timed-out ≠ unreachable). Billing-half is PLAUSIBLE (unverified because no outbound probe of EachLabs' billing-at-accept semantics was possible from this localhost-only box); the false "unreachable" message is CONFIRMED by the code path.
Fix: distinguish abort/timeout from network failure in the message ("eachlabs prediction create timed out - it may still have been created and billed"), and let the caller/refund path treat retries accordingly.

**[LOW] `listEachLabsModels` trusts the response shape — non-JSON 200 leaks a raw SyntaxError; a wrapped payload crashes the mapper with TypeError** — `line 72` (+ `line 47`)
What: line 69's `.catch(() => null)` guards only the fetch; `await res.json()` on line 72 is unguarded, and the result is cast to `RawElModel[]` with no `Array.isArray` check. A 200 with an HTML/empty body rejects with a raw `SyntaxError: Unexpected token ...`; a shape drift to `{ models: [...] }` makes `for (const m of list)` (line 47) throw `TypeError: list is not iterable`.
Trigger: edge proxy / Cloudflare interstitial on 200, or EachLabs wrapping the list (header comment says bare array was grounded live 2026-08-22 — works today; this is the drift case).
Impact: no server crash (`vite.eachlabs.ts:62` catches and 502s) but the surfaced message is junk like "Unexpected token <", and the failure mode is a confusing cast-crash rather than a diagnosable error. CONFIRMED as an unguarded path; the wrapped-payload case is PLAUSIBLE (depends on API drift).

## Missing safeguards

- No cancellation seam: `runEachLabsModel` takes no `AbortSignal` and no prediction-cancel call — a stopped film keeps polling to the 10-min deadline and the paid cloud prediction keeps running; nothing ever issues a cancel on timeout/abort either.
- Fixed 3 s poll cadence with no jitter or backoff (line 92) — actively consumes the account's documented per-minute request slots while polling.
- Terminal-status allowlist is closed (success/failed/error/canceled only, lines 95/100): any unrecognized terminal status (e.g. a "cancelled" spelling or new enum value) falls through to the false-timeout path; an unseen status should at least be surfaced in the timeout message.
- No runtime validation of the models response (`Array.isArray` + element shape) at line 72/47; the repo's own doctrine elsewhere (bundles schema) validates external payloads at load.
- The spend ledger never sees EachLabs prices: `ElModelUi.p50Usd` is computed for exactly this, but the only film consumer records the voice leg with `null` cost (`vite.film.ts:1022` `recordSpend(..., null)`) — spend tallies read 0 for real cloud money.
- `src/providers/eachlabs.test.ts` covers failure-status surfacing but has no case for poll-level HTTP errors (404/401/429) or a non-JSON models body — the HIGH/MEDIUM findings above are all untested edges.

context-pack: consumers vite.eachlabs.ts:44 (proxy /run) and vite.film.ts:1001 (genVoice, autopilot paid voice leg; denylist is per-engine so path is live); git shows the file unchanged since c588bdd; sha matches the 2026-08-27 "Clean" review, which recorded no findings.
new-findings: 4
