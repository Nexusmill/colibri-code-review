# Review - bug mode

- source: src/providers/openrouter.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: readSseLines + consumeChatStream + openRouterChatStream added)
- context pack: callers traced (vite.agent.ts callBrain cloud path, vite.film.ts
  askBrain, src/llm/client.ts agentChatStream, src/api/film.ts
  autopilotDraftStream); the sidecar dialect verified live against the running
  llama.cpp build before wiring; unit tests in openrouter.test.ts cover the
  parser's edge cases.

## Verdict

Shippable. The accumulator is the wave's foundation and every consumer goes
through it; its edge cases are unit-proven and its live dialect was probed
before wiring rather than assumed.

## Bugs & vulnerabilities

None CONFIRMED. Adversarial pass results:

- **Tool-fragment merge by index** - CONFIRMED correct against the live
  sidecar probe (first fragment carries id+name, later fragments argument
  pieces; merge reproduces `{"query":"vram"}` exactly).
- **Usage capture** - CONFIRMED on the live sidecar (final empty-choices
  chunk) and on the live cloud route (done event carried 1038->39 tokens,
  $0.00162). `stream_options.include_usage` accepted by all three endpoint
  families probed.
- **Torn/split chunks, CRLF, missing [DONE]** - CONFIRMED by unit tests
  (three cases); a half answer with its truth beats a hang, by design.
- **Empty-token filter** `t.id !== "" || t.function.name !== ""` - traced:
  fragments without id AND without name never occur in the probed dialect;
  a hypothetical all-arguments fragment would drop the call rather than
  crash. PLAUSIBLE-only, no provider observed doing it.

## Missing safeguards

- SSE spec allows multi-line `data:` events (joined with \n by strict
  consumers); no OpenAI-compatible provider emits them and none of Caliper's
  own emitters do - documented payload-per-line contract, not a defect.
- No consumer-side abort on hang (matches the pre-wave fetch behavior; the
  console's elapsed heartbeat and RETRY supersession are the app's answer).
