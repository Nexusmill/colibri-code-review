# Review - bug mode

- source: src/components/FilmWizard.tsx
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: runDraft streams phases into the status line; a
  per-second elapsed ticker rides the drafting state)
- context pack: the live-progress owner rule (per-second ticking timer);
  the status render sites (three `{status || fallback}` lines); the
  critique/fail paths read in full; the live draft probe's phase stream.

## Verdict

Shippable. The ticker composes with phase events instead of fighting them
(phaseRef holds the latest phase; each tick re-renders `phase · Ns`).

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- the effect cleans up on !drafting and clears phaseRef - no stale ticker.
- phase events land immediately (setStatus(p)) and the next tick stitches
  the seconds on; no string surgery on arbitrary status text.
- the critique-gate and failure paths are unchanged - runDraft's tail was
  not touched.

## Missing safeguards

- None beyond the server-side note (a reload mid-draft loses the POST -
  pre-existing, out of this wave's scope).
