# colibri bug review - src/stores/routesStore.ts (delta)

source: src/stores/routesStore.ts · reviewer: ZCode GLM-5.3 in-session · sha256 e148531d (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 136b501d @ 73feb2b 2026-08-22)
context: diff 4+1; prior review 136b501d carried; pairs with gatedRouteConfig server-side.

## Verdict

Shippable - profile surfaced into the store from the server config (single truth).

## Bugs & vulnerabilities

None new (profile hydrated from getRoutes().config.profile; default multimodal matches DEFAULT_CONFIG).

## Missing safeguards

- none new.

## Fixed since last review

- (prior had no open findings)
