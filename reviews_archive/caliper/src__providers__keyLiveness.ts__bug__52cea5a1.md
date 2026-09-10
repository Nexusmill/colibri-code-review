<!-- colibri review
source: src/providers/keyLiveness.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 52cea5a1cd79d78c11cf310b4253c00b02a10c5efcc4c7655a53fad18028ed8d
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable. The probe table (six services, each url grounded in the service's docs or the repo's own adapter - grounding notes in the header comment) plus the fixed verdict vocabulary. The 404-is-never-dead rule and the OpenRouter key-label guard are the two judgment calls, both deliberate and both tested.

## Bugs & vulnerabilities
(none confirmed)

## Missing safeguards
- **[LOW] account strings render unsanitized** - they land in a chip textContent and a title attribute (React escapes both); no injection path found.
- **[NOTE] spacexai rides an undocumented models endpoint** - a 404 there degrades to "endpoint away" rather than guessing; if x.ai documents a key-info endpoint later, the table is one line.
