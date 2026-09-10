# Review - bug mode

- source: src/vram/preflight.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (new file)
- context pack: consumers vite.caliper.ts handlePreflight + src/api/client.ts
  getVramPreflight; the corpus writer's formats (appendMeasured heading
  `## <title> [tags] — <date>`, the bench footprint sentence built from
  summarizeVram); /caliper_vram.py payload (torch.free/total, 503 on
  degraded counters); five unit tests.

## Verdict

Shippable. Pure functions, fixed verdict vocabulary, basis always spoken.

## Bugs & vulnerabilities

- **[FIXED IN-WAVE] heading-prefix contract gap** - the parser matched
  an invented lowercase heading while the writer emits
  'Bench: <bundle> <param> <a> vs <b> (seed N)' (the adversary's
  verify-the-external-contract item was a real catch): the estimate
  would have stayed inert forever even after benches ran. Fixed against
  the writer's bytes + a contract-lock test that fails loudly on drift.

None CONFIRMED. Traced:
- section prefix `bench <bundle> ` cannot prefix-confuse (test:
  Anima-Turbo-Pro does not ride Anima-Turbo entries).
- newest entry wins (append-only corpus, last word = newest measurement).
- free <= 0 (degraded zeroed counters) is treated as no data, not 0 GB -
  matches the node's own degradation contract.
- thresholds: fits needs 15% headroom (allocator + ComfyUI's own reserve),
  tight is within that band, over below the measurement.

## Missing safeguards

- The measured footprint is ALLOCATED after a bench's cold load; a queue
  with resident models swapping may need more than the delta - the spoken
  line carries resident count so the human can reason; documented, not
  hidden.
