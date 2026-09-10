# Review - bug mode

- source: vite.agent.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: stream mode on /api/agent/chat, streaming callBrain,
  phase/delta/discard/done/error events, extractToolCallMarkup wiring)
- context pack: ScreenStage's agentChatStream consumer contract; the JSON
  mode's byte-parity requirement (harness optimizer-cloud-brain probes it
  raw); the apply/undo/analyze routes untouched; sidecar dialect probed
  live; screenshot evidence mid-stream and landed.

## Verdict

Shippable after one live-caught defect was fixed at the root (the sidecar
markup leak, below). The event protocol's failure ordering was the highest
risk and traced clean end to end.

## Bugs & vulnerabilities

- **[FIXED THIS WAVE] sidecar tool markup leaked as the visible answer** -
  CONFIRMED live (screenshot: `{"name": "read_vram", "arguments":
  {}}</tool_call>` rendered as prose). Root cause: llama.cpp's incremental
  parser misses the `<tool_call>` span occasionally (intermittent - a
  direct repro stayed clean while the real TOOLS payload leaked once).
  Fix at the adapter layer: extractToolCallMarkup (src/llm/tools.ts)
  recovers complete spans into real calls; the loop then executes the tool
  and the existing discard retraction covers the already-streamed text.
  Post-fix live rerun: landed reply clean, tool round executed, unit tests
  15/15.

Ordering traces (all CONFIRMED clean):
- 405/400/503 fire BEFORE the SSE headers flush - the client's !res.ok JSON
  error handling is unchanged in both modes.
- A 429 cannot double-stream deltas: the status arrives before any body,
  so the fallback retry starts from zero forwarded text.
- discard is emitted only when a round that streamed deltas turns out to
  carry tool calls; the client reverts to the phase row.
- respondWith parity: the done event spreads the exact JSON payload
  (brain/model/tokens/costUsd/note) - verified live on both transports.
- Local usage accumulation from the streamed final chunk - verified live.

## Missing safeguards

- The nudge leg (demand-proposals retry) intentionally does not stream
  deltas - its words are appended to `reply` and superseded wholesale by
  the done event; noted so a future reader does not "fix" it.
