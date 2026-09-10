# Review - bug mode

- source: src/components/ScreenStage.tsx
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: send/runAnalysis stream through agentChatStream; live
  answer text + server phase line states; busy row renders the arriving
  words with the pulse)
- context pack: the console persistence contract (caliper.console,
  restore-drops placeholders, applied-index remap) re-read in full; the
  runId supersession pattern; screenshot evidence mid-stream and landed.

## Verdict

Shippable. The streaming text deliberately never enters `turns` - the
persistence contract is untouched by construction, which was the riskiest
interaction here.

## Bugs & vulnerabilities

None CONFIRMED. Traced:
- a close mid-stream cannot persist a partial answer as a complete turn
  (live/phaseText are component state; turns mutate only on done/error).
- runAnalysis callbacks guard on runId; a superseded run's finally still
  clears only its own run (the `runId.current === id` check).
- onPhase ignores phases once deltas flow (`if (!shown)`); after a discard
  the phase line resumes - matches the server's retraction semantics.
- the old `{"name":"…","content":"…"}` placeholder turn is gone; the
  restore-drop for dangling "…" turns remains harmlessly for legacy stores.

## Missing safeguards

- Auto-scroll follows the stream at the 1s elapsed cadence, not per delta -
  deliberate (per-token scroll thrash); the words + pulse are the life.
