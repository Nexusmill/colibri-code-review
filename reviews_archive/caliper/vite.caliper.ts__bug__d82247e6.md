<!-- colibri review
source: vite.caliper.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: d82247e65cc939f59dbe02291198490aa5149ce9a9a6f19e8eee22a39059ddce
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable. Delta: node:crypto import, canonicalNodePath const, handleNodeSync (GET identity from the repo's canonical node copy), one route registration beside /api/preflight. Verified live: /api/node-sync answers {name, version, 64-hex sha} through the restarted preview.

## Bugs & vulnerabilities
(none confirmed)

- REFUTED in pass 3: "regex could match a commented-out _NODE_VERSION" - the canonical file has exactly one occurrence (the assignment); a second would have to be introduced by an edit that also changes the sha, which is the drift this endpoint exists to surface.

## Missing safeguards
- **[LOW] method-agnostic handler** - handleNodeSync answers POST/PUT identically to GET. Idiom-consistent with the /api/preflight inline handler (read-only, no writes, no secrets); not worth a method gate.
