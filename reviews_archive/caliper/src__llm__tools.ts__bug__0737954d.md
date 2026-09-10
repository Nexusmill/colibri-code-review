# Review - bug mode

- source: src/llm/tools.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: extractToolCallMarkup added)
- context pack: consumer is vite.agent.ts's sidecar adapter only; the
  validateToolCall contract downstream of recovered calls; three unit tests
  in tools.test.ts (leak case, nested args + multi-span, malformed spans).

## Verdict

Shippable. The regex anchors on the literal closing tag so nested braces
cannot trip it; malformed spans stay as the model's words rather than being
silently eaten.

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- non-greedy `[\s\S]*?` with the `\s*</tool_call>` tail anchor captures
  through nested braces to the tag - test-proven with a set_param body.
- spans whose JSON lacks name/arguments stay verbatim (test) - honest over
  lossy.
- ids are synthesized (`leaked-N-timestamp`) - validateToolCall keys on
  name/args, ids only need loop uniqueness.

## Missing safeguards

- A span with STRINGIFIED arguments (`"arguments": "{...}"`) stays visible;
  validateToolCall would have accepted it had it arrived structured.
  Rare in the probed dialect; noted as PLAUSIBLE, not wired around.
