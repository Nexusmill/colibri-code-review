# colibri bug review - src/film/analysis.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 067464be - 2026-08-26
mode: bug - context: analysis.test.ts (synthetic click tracks/envelopes); consumers vite.film create/autopilot-draft (decodeSong -> analyzePcm, shotGrid coverage math); read end to end

## Verdict

Shippable - no confirmed defects. The DSP core earns its unit-testability claim.

## Bugs & vulnerabilities

None confirmed. Refuted in the adversarial pass:

- Zero-width or reversed shot slots from beat-snapping: impossible by arithmetic - grid sub-spans are >=2.5s (count = round(span/5)), each boundary snaps within 0.35s of its raw value, so adjacent snapped boundaries cannot cross or collapse; section spans are >=3s by the novelty guards.
- beatGrid's fractional refinedHops loop can round a center one past flux's last index - yields a harmless time value beyond the envelope, never an index error (flux[at]! comparisons degrade to false).

## Missing safeguards

- detectTempo's autocorrelation is O(n·lags) over the whole flux - fine at 23ms hops for minutes-long songs on this machine; no guard against pathological (hours) inputs.
