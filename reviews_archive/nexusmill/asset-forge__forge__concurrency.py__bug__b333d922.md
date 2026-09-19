# Colibri Review - bug (FULL re-audit) - asset-forge/forge/concurrency.py

- **Source path:** `asset-forge/forge/concurrency.py` (twin `asset-forge-user/forge/concurrency.py` byte-identical, G23)
- **Reviewer:** claude-fable-5-1 fork (in-session), Colibri G37 protocol, campaign item 1 (AF units), rank 41
- **sha256 reviewed:** `b333d9229113fbaa04294d7bf91c85e9c6d32d9560ab2b1f1da609cbf064f49a` (sha8 `b333d922`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 08-04 `2571d7f5` bug record and the `b333d922` fix record predate the adversarial gate and are untrusted - no delta against them)
- **Context pack:** jCodemunch outline (resolve_workers, RateGate, Stop, imap_bounded/_one, map_bounded, retry_after_seconds); callers scanned: library_gen.py (gate/stop at 969-970, `gate.wait(stop)` before every paid call at ~1015 and 1158, `penalise(retry_after_seconds(...))` at 1059/1197, `imap_bounded` consumer at 1307-1322 treating `(value None, exc None)` as "stays pending"), bundle.py (`map_bounded` at 332 with the all-or-nothing assembly at 333-339, `Stop.trip("error")` at 327); remediation rows GROK-CC (four findings), CKPT-STREAM, CONSUMER-ABORT, the test-rot row; feature rows AF-CONC-SAFE and AF-ABORT-WINDOW (contracts pressed); battery grok_cc_threading.py 13/13 re-run on the current bytes; this morning's AF-LG-CKPT-SHARE (library_gen) for the attribution this module's `finally` produces.

## Verdict
Clean - 0 confirmed. The 208 lines were read end to end and every claim the callers rely on holds at the bytes: the bounded pool, completion-order streaming with the index carried, the never-started `(i, item, None, None)` tuple that the consumer leaves pending, first-writer-wins `Stop.trip` with `set()` inside the lock, `RateGate.wait(stop)` abandoning a throttle pause the instant the run dies, the consumer-abort `finally` that trips `"consumer"` and cancels every not-yet-started future (started ones finish - the documented in-flight blast radius), and `retry_after_seconds`' explicit-seconds regex that a hint can only extend.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards
- `imap_bounded` submits every item's future up front; with a stopped run the queued `_one` calls each still take a pool slot to return the never-started tuple. Cost is microseconds per item; noted for completeness.
- `as_completed` has no overall deadline; a provider call that never returns holds its worker forever. The provider's own create/poll timeouts are the bound (PS-TRANSPORT class, in the provider), not this module's.
- `resolve_workers` raises `ValueError` on a non-numeric `requested`; no caller passes user input (library_gen and bundle pass `None` or an int from code), so the raise is unreachable from the API today.

## Adversarial verification pass (refuted claims)
- "`RateGate.wait(stop)` returns False when the gate is already open even if `stop` is set, letting one more paid call through" - refuted: both library_gen call sites check `stop.is_set()` immediately before `gate.wait(stop)` (1155/1158 and the first-call ladder), exactly the contract the docstring states ("Callers treat True exactly like a pre-wait stop check").
- "The consumer-abort `finally` can mis-attribute a credit trip as `consumer`" - refuted: `Stop.trip` is first-writer-wins; a worker's earlier `credit`/`auth` trip keeps its kind, the `finally`'s `consumer` trip is a no-op then.
- "A consumer exception (not an explicit close) leaves the generator suspended and the queue draining paid calls" - refuted: CPython drops the for-loop's iterator reference during unwinding, `close()` raises `GeneratorExit` at the `yield`, the `finally` runs - the CONSUMER-ABORT row's own 12/12 reproduction was of the pre-fix bytes; the current bytes are what this morning's library_gen fork observed tripping `consumer` on a PermissionError.
- "`retry_after_seconds` reads '1st' or '500ms' as a hint" - refuted at the regex: `\b(\d+(?:\.\d+)?)\s*(?:s|sec|secs|second|seconds)\b` needs a word boundary after the unit ('1st' has none) and a boundary before the digits ('500ms' offers only 'ms').
- "`penalise(nan)` poisons `_until`" - refuted: `max(self._until, now + nan)` keeps `_until` (Python `max` returns the first argument on a nan comparison) and `retry_after_seconds` never returns nan.
- "`map_bounded` misreads a never-started item as a produced item with value None" - refuted: bundle filters `v is not None` and raises "bundle aborted: k of n items produced"; the abort receipt names every billed prediction id.
