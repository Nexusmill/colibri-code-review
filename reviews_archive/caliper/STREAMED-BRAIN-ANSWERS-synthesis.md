# Synthesis - the streamed-brain-answers wave (2026-09-06)

Nine single-file units reviewed in bug mode against the staged delta; one
synthesis, ranked:

1. **[FIXED IN-WAVE, CONFIRMED live] The sidecar markup leak** - the only
   defect that escaped into a rendered screen: llama.cpp's incremental
   tool parser intermittently misses the `<tool_call>` span and the raw
   JSON rides into content as the visible answer. Fixed at the adapter
   (extractToolCallMarkup, deterministic core, 3 unit tests), verified by
   a post-fix live rerun plus screenshots.
2. **[FIXED IN-WAVE] Dead transports** - agentChat and autopilotDraft had
   zero consumers after the switch; deleted per the repo's dead-data
   doctrine. The unchanged bundle hash proves tree-shaking had already
   excluded them.
3. **[HARDENED] Seat-dependent harness test** - optimizer-cloud-brain
   implicitly required the cloud brain to be the seated one; any actor
   leaving local seated failed it misleadingly. Now seats openrouter
   explicitly and restores.
4. **[VERIFIED, not defects]** Three cross-cutting traces: pre-event error
   ordering stays JSON in both modes; the 429 fallback cannot double-stream
   deltas; the console's persistence contract is untouched because
   streaming text never enters turns.

Residual (accepted, named): no client-side abort on a stalled stream
(matches pre-wave fetch exposure; heartbeat + RETRY supersession cover it);
a page reload mid-draft still loses the POST (pre-existing; a resumable
background job is a separate commission).

Evidence: tsc clean, vitest 426/426, harness fast tier 56/0/4 (streamed
test PASS live on the local brain), cloud transport verified live by hand,
a real draft streamed end to end on the 4B including the honest anchor
refusal, screenshots mid-stream and landed.
