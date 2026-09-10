<!-- colibri review
source: vite.keys.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 5e7938407f3a948ee098850d755ee578afdfecba45c2cacb6ae36dafac667c15
date: 2026-09-06
mode: bug
context: E-2 wave (key liveness + stale routes); live-verified through :4173 (three real probes, stale flag + restore); delta reviews vs prior shas
-->

## Verdict
Shippable. Delta: /test branch ahead of the existing GET/POST - server-side key read (the key never crosses to the browser), Bearer probe with a 10s timeout, JSON-parse-or-null body, verdict mapped through the shared pure function. 405 on non-POST, 400s for unknown ids and keyless services with their errors spoken.

## Bugs & vulnerabilities
(none confirmed)

- REFUTED in pass 3: "the /test branch could shadow the key-set POST" - connect strips the mount prefix, so only url.pathname === "/test" enters the branch; the exact /api/keys POST falls through unchanged (verified against the eachLabsRoutes mount idiom).
