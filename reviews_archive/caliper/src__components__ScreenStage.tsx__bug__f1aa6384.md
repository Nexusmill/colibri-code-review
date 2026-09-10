# Review - bug mode

- source: src/components/ScreenStage.tsx
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: picker gains catalog get-it rows with size + ctx
  ceiling; switchBrain speaks the download note; shelf rows for
  catalog-known files speak their ceiling)
- context pack: the native select's option-text-only rendering (hints
  live in the label for get-it rows); the live harness DOM assertion.

- **[FIXED, adversary round 2] refusals presented as success** -
  switchBrain checks r.started before any note; a 409 now speaks its own
  error, the download note still returns early.

## Verdict

Shippable. Rows are data-only additions; the download branch returns
before the note so no stale note lingers.

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- get-it rows filter through isCatalogBrain (embedder/reranker never
  offered as brain seats).
- a 202 downloading answers with its own note and returns - the seated
  brain is untouched until the user re-picks the landed file.
- the ceiling text divides by 1024 and rounds - 262144 -> "256k ctx",
  truthful shorthand.

## Missing safeguards

- The native <select> cannot render row hints - the get-it label carries
  size + ceiling inline; verified by DOM assertion (a closed select
  screenshot cannot show the list).
