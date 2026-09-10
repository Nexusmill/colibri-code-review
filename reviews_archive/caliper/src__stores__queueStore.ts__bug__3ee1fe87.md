# Review - bug mode

- source: src/stores/queueStore.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: Job.preflight field; queue() takes the pre-flight
  reading before queuePrompt and carries it on both job exits)
- context pack: the queueInFlight busy contract (the TOCTOU note);
  saveProvenance untouched (preflight deliberately not persisted - it is a
  queue-time estimate, not provenance); DeckControls render.

## Verdict

Shippable. The estimate never gates and never blocks: a failed fetch is
swallowed (no estimate beats a fabricated one), and the reading lands on
both the rejected and queued job rows.

## Bugs & vulnerabilities

None CONFIRMED. Traced: the preflight fetch sits inside the
queueInFlight=true window (still single-flight - no double-queue window
opened); the rejected job carries the preflight so a constraint-rejected
press still speaks its VRAM truth if it had one.

## Missing safeguards

- The reading is taken BEFORE queuePrompt (pre-flight by definition); the
  free number can drift by the time the server loads models - the spoken
  line says "at queue time" context via its date/basis wording. Accepted.
