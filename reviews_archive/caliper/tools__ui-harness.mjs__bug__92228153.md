<!-- colibri review
source: tools/ui-harness.mjs
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 922281535d2c18f9b4c7731025cb3fe6a27884320182b6cfc0e0ee0efd7e84e1
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable after two in-pass syntax fixes (TypeScript annotations in a plain .mjs - node --check is now part of the wave discipline). Delta: settings-keys gained the TEST-key presence check; settings-key-liveness probes the vocabulary cold (unknown id 400) and live (present key, honest skip when keyless); settings-stale-routes drives a probe slug through the real UI and RESTORES the owner's image route on every exit path, re-reading it after.

## Bugs & vulnerabilities
(none remaining confirmed)
