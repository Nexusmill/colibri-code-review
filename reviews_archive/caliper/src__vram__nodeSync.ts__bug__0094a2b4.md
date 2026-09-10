<!-- colibri review
source: src/vram/nodeSync.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 0094a2b48f14179ac8183d16bc194b1ed422c81e3b5c1388a0da74a0c6c1e1ca
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable. Pure verdict function; 4-case contract vitest-proven (silence / in-sync / drift / pre-self-id). Version fallback chain verified: in-sync prefers canonical.version, falls back to deployed.version (non-null per CaliperVram.node), so a regex-missed canonical version still renders a real version string.
