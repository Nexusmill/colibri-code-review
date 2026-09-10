# Review - bug mode

- source: vite.film.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: askBrain streams with exact word counts; the
  autopilot-draft action gains an SSE mode with phase/word/judge events)
- context pack: FilmWizard's autopilotDraftStream consumer; the draft
  block's existing critique gate / world re-asks / adversary loop read in
  full; live draft probe captured the whole event stream including the
  honest error path.

## Verdict

Shippable. The SSE wrapper sits outside every pipeline decision - the
brain/judge/validation logic is untouched; the live probe walked critique ->
world -> timeline -> storyboard word ticks -> judge -> re-draft -> anchor
refusal, every phase arriving as designed.

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- id validation and the 404 run-read fire before SSE headers - error paths
  stay JSON for the non-stream client.
- finishDraft/error-event parity with send(200)/send(400) in both modes.
- askBrain's fallback retry resets the word accumulator per callChat
  invocation (acc is call-scoped), so counts never carry across attempts.
- wordTick throttles at >=25 words so the status line ticks without
  per-token chatter.

## Missing safeguards

- A page reload mid-draft still loses the in-flight POST (fetch dies with
  the page) - pre-existing behavior, unchanged by this wave; the
  live-progress rule is satisfied by phases + word ticks + the wizard's
  elapsed counter. A resumable background job is a separate commission.
