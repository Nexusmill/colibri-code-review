<!-- colibri review
source: src/surfaces/BundlesSurface.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: f1d1976984d83bc54a48d2ecd72bd6a43d4a6001ff388a22cb8f2df698bc1deb
date: 2026-09-06
mode: bug
context: E-6 wave (bundles idiom+copy, graph restore-by-timestamp+drift, palette verbs+legend, docview code+find); the stale-dist incident and its healing
-->

## Verdict
Shippable. remove arms per-bundle (5s window, timer cleaned on unmount) and fires on the second press; duplicate opens the editor on a uniquified named copy with empty id (the schema's migration assigns a fresh unique id at save - verified against the schema's taken-set loop). The arm test asserts the store is untouched between presses.

## Bugs & vulnerabilities
(none confirmed)
