source: src/stores/queueStore.ts
reviewer: tencent/hy4-preview (scan ladder hunt T2)
sha256: ca3464c62abc37810fc05af60db12df6c671e8f5bb6fc0910b7041ac776e13e5
date: 2026-09-19 13:04
mode: bug
context: queue store; BUGHUNT10/12 race laws excluded

2 findings, BOTH REFUTED with evidence:
- [HIGH] "empty nodeErrors throws TypeError in the rejected-prompt branch" - REFUTED against JS semantics: `first?.[1].errors[0]?.details` cannot throw; optional chaining short-circuits the ENTIRE chain to its right, so an empty map yields undefined and the ?? falls to result.message. The exact case (empty node_errors + message) is already pinned GREEN in stores.test.ts line 106-110. A doctrine comment now names this at the site.
- [HIGH] "clearAll does not interrupt the running render" - REFUTED against api/client.ts: clearQueue() (which clearAll awaits) is "the wedge cleaner: drop everything pending and interrupt whatever is running" - it POSTs the queue clear AND awaits interrupt() (lines 140-151).
Scan log: %TEMP%/hunt2/stores__queueStore.md
