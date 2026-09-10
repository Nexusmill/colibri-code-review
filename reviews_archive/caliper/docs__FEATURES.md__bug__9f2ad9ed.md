<!-- colibri review
source: docs/FEATURES.md
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 9f2ad9ed9b69c521873db7258e25eed0b876a3c952d14fbdea2dd1b7fbe453ef
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable. Three rows (settings-key-liveness, settings-stale-routes new; settings-keys amended for TEST); parity enforced by the tier's manifest gate, which failed closed on the missing id before the test existed.
