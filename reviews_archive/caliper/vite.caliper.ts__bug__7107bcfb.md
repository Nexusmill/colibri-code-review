# Review - bug mode

- source: vite.caliper.ts
- reviewer: in-session colibri v0.2.0 (GLM-5.3, full repo context)
- date: 2026-09-06
- mode: bug (delta: /api/preflight route + handlePreflight)
- context pack: the middleware's URL-parsing idiom (graph-exists /
  graph-backups routes); COMFY_URL; the node's 503-on-degraded contract;
  live route check through the preview proxy.

## Verdict

Shippable. GET route, JSON out, every failure degrades to an honest
verdict.

## Bugs & vulnerabilities

None CONFIRMED. Traced: corpus read failure -> empty string ->
no-measurement; backend away/503 -> backend-away; bundle param is
length-capped. Verified live through :4173 (answered no-measurement for an
unbenched bundle - truthful, the corpus has no bench entries yet).

## Missing safeguards

- No cache on the /caliper/vram read (4s timeout per request) - the
  preflight fires once per queue press, not on a poll; fine as built.
