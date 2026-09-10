# Review - bug mode

- source: src/llm/client.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: agentChatStream added; agentChat deleted - zero
  consumers after the console switched)
- context pack: consumer ScreenStage (send + runAnalysis with runId
  guards); server protocol from vite.agent.ts; readSseLines shared with the
  provider transports.

## Verdict

Shippable. The client mirrors the server protocol exactly; deleting the
dead JSON twin honors the repo's dead-data doctrine (the bundle hash was
already unchanged - tree-shaking had excluded it).

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- !res.ok reads the JSON error (pre-event failures), an error event throws
  the same way mid-stream, and a stream that ends without done throws -
  three exits, all surfaced to the caller as Error.
- unknown event types are ignored (forward compatibility).

## Missing safeguards

- No client-side abort if the stream stalls - same exposure as the
  pre-wave fetch; the console's heartbeat/RETRY supersession covers it.
