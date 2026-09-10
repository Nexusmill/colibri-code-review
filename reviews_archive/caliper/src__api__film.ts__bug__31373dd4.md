# Review - bug mode

- source: src/api/film.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: autopilotDraftStream added; autopilotDraft deleted -
  the wizard was its only consumer)
- context pack: FilmWizard runDraft; the server's done-event payload shape;
  readSseLines shared.

## Verdict

Shippable. Same contract as the console client: three error exits, phase
callback, done payload typed as the record (+critique flag).

## Bugs & vulnerabilities

None CONFIRMED.
