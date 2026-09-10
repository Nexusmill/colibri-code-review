<!-- colibri review
source: src/api/client.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 3477ebb6728d037e5c288b1703fffe41faa5131adaaebf18905bd3aff2369ff2
date: 2026-09-06
mode: bug
context: E-4 wave (queue/deck quality batch); copy-diagnostics verified live with clipboard result; etaMs live null-with-basis
-->

## Verdict
Shippable. getQueueEntries decodes entry[2] through the pure helper; QueueEntry.nodes additive.
