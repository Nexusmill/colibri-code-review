# Review - bug mode

- source: src/api/client.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: getVramPreflight)
- context pack: consumer queueStore.queue (catch -> undefined, never blocks).

## Verdict

Shippable. Thin fetch wrapper, encoded query, throws on !ok, caller
swallows by design.

## Bugs & vulnerabilities

None CONFIRMED.
