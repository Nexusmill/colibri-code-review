# Review - bug mode

- source: src/llm/client.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: llmStart returns { started, downloading? })
- context pack: both callers audited (DeckControls awaits and ignores the
  value; ScreenStage reads downloading) - no truthiness-on-boolean caller
  remains.

- **[FIXED, adversary round 2] the refusal half of the payload was
  unread** - llmStart now returns started:false with the server's own
  error text on !ok; switchBrain shows it instead of a success note.

## Verdict

Shippable. Structured return, 202's body surfaced, callers verified.

## Bugs & vulnerabilities

None CONFIRMED.
