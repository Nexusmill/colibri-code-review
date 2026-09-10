<!-- colibri review
source: src/api/client.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: e5904c0d41c87aa6344907e8da1fe9e8f168b4f3d70378201375d10f287cef6a
date: 2026-09-06
mode: bug
context: E-6 wave (bundles idiom+copy, graph restore-by-timestamp+drift, palette verbs+legend, docview code+find); the stale-dist incident and its healing
-->

## Verdict
Shippable. The graph backup listing returns backups+drifted; the restore passes the optional file. Callers updated in the same change.
