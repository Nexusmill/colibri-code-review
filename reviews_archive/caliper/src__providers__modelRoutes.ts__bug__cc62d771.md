# colibri bug review - src/providers/modelRoutes.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 cc62d771 - 2026-08-26
mode: bug - context: shared by vite.routes.ts (server resolution, film engine) and the client store/picker; setProfile's server behavior verified against resolveRoute

## Verdict

Shippable - no defects.

## Bugs & vulnerabilities

None confirmed. The one suspect - resolveRoute returning a stored LOCAL route verbatim under a cloud-only profile - is unreachable: vite.routes.ts line 97 wipes routes to {} on the cloud-only switch, so no stored local route survives to be resolved.

## Verified-correct

- validateRoute's three-way contract (cloud-only rejects local; local must be on the shelf; cloud needs service+model); the cloud fallback's undefined cloudModel (every consumer checks route.cloudModel before use); typeDef's unknown-type throw.
