# Colibri fix-pass record - asset-forge/forge/concurrency.py (GROK-CC)
- source: asset-forge/forge/concurrency.py
- model: claude-fable-5 (in-session)
- sha256: b333d9229113fbaa04294d7bf91c85e9c6d32d9560ab2b1f1da609cbf064f49a
- date: 2026-08-15
- mode: fix (GROK-CC all four findings)
- context pack: prior review asset-forge__forge__concurrency.py__bug__2571d7f5.md; both gate.wait
  call sites read in library_gen (_attempt ~978, black-frame loop ~1093 - stop checked BEFORE the
  wait in both, confirming the docketed window); deferred_manifest GROK-CC.

## Verdict
All four findings re-verified CONFIRMED against 3b9bbc9a (unchanged since dispatch) and fixed;
callers updated in the same tranche so the stop-aware wait is actually consumed. Probe
grok_cc_threading.py 13/13 (live threading, not source asserts). Twins byte-identical.

## Fixed since last review
- GROK-CC #1 post-abort charge window -> stop-aware RateGate.wait + both call sites
- GROK-CC #2 trip event set outside lock -> set inside the first-writer-wins block
- GROK-CC #3 retry-hint regex ('1st' -> 1s) -> explicit seconds shape + exponential floor kept
- GROK-CC #4 unguarded future submission -> submission inside try/finally
