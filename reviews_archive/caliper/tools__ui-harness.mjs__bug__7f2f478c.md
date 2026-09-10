# Review - bug mode

- source: tools/ui-harness.mjs
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: streamed-brain-answers tier entry; optimizer-cloud-brain
  seats openrouter deterministically and restores the seat)
- context pack: the tier runner's skip() discipline; the seat-flip incident
  that motivated the deterministic seating (a locally-seated rig failed
  the cloud probe with a misleading "no reply/cost").

## Verdict

Shippable. The new entry asserts the transport contract (content-type,
waking phase, done reply, nothing after done) with honest skips when no
brain is available.

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- the cloud seat is restored only when the original was local - the rig's
  observed default; other cloud brains are left seated (out of this rig's
  world, noted).
- the events-after-done check guards the ordering contract cheaply.

## Missing safeguards

- The wizard's draft stream has no tier entry by design - a real draft is
  a live-brain check (the same ruling as THE PLAN's draft affordance); the
  transport is covered by the console entry plus the accumulator's tests.
