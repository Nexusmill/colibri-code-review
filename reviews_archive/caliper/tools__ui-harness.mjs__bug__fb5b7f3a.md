<!-- colibri review
source: tools/ui-harness.mjs
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: fb5b7f3a49074bb64616302f3f90c91a130642adeb8f4f46a8becd535a72d385
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable after two in-pass fixes. Delta: node-self-id fast-tier test (canonical identity validation + live drift comparison when the backend answers).

## Fixed since last review (this session, pre-commit)
- The skip/log line said "backend away" even when the backend was UP but its node predates self-id - now a three-way honest log (matches / pre-self-id / away).
- Test id was `node-sync` while the manifest row is `node-self-id` - the harness parity gate failed the tier (exit 1, MANIFEST GAP both directions); renamed to match. Tier now 59/0/4 exit 0.

## Bugs & vulnerabilities
(none remaining confirmed)
