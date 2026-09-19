<!-- source: src/film/autopilot.ts | reviewer: zcode-glm-5.3 | sha256: d15ba2c183791bf6fb8d67f38c08a778545d14376717f2a91357619517a9e847 | date: 2026-09-15 | mode: bug -->
<!-- context: owner commission 2026-09-15 'do them all': the six-item batch (win-rate sample honesty, EXPENSIVE audition truth, install size+sha verify, sidecar ctx serve, VRAM cmdlines, bundle export/import verified-already-shipped). Evidence: tsc 0, vitest 508/508 (57 files), build OK, fast tier 77/0/7, live /caliper/vram 1.2.0 with cmdlines, offline-grounded pins. -->

## Verdict
Shippable - two truth fixes, both pinned.

## Fixed since last review (this delta)
- **[per commission] win-rate sample honesty**: winRatesFromRuns returns {rate, n}; resolveLadder's winOf demands MIN_SAMPLE=2 - a single lucky 5-star run no longer outranks a verdict repeated across runs (red-green-style pinned: the anecdote test fails against the naked-rate ordering).
- **[per commission] the EXPENSIVE note speaks the audition truth** - same $0.08/s at both seats; the savings are the finishes never bought on rejects (full $0.13/s at 2K).

## Bugs & vulnerabilities (delta)
- None. The gate composes with the balanced proven-threshold (winOf >= 3.5) and the best sort identically.
