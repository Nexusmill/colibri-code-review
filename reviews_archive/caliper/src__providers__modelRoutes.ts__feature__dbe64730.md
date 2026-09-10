# Colibri review — src/providers/modelRoutes.ts (feature)

- **Source:** `src/providers/modelRoutes.ts` · **sha256:** dbe64730
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 5 importers (api/catalog, api/modelRoutes, DeckControls, vite.routes); FEATURES.md rows `replicate-models`, `generate-source-select`; the 2026-09-02 gate finding history recorded in `gatedRouteConfig`'s comment; last touch 91620a1 (2026-09-02).

## What this module does

The universal model-routing core, pure logic: the five `GenType`s with shelf/category/runnability metadata, `Route`/`RoutesConfig`, `validateRoute` (profile- and shelf-aware: cloud-only rejects local; local must name an installed model), `resolveRoute` (local-first when the shelf has candidates), and `gatedRouteConfig` — the cloud-only gate that enforces the READ path while preserving stored local routes for restoration.

## Suggested add-ons

**Stale-route detection against live catalogs** — Value Med-High · Effort S-M
- What: a `checkStoredRoutes(config, cloudCatalogs)` returning per-type warnings when a stored `cloudModel` no longer exists in its service's live catalog (catalogs already flow through `listCloudModels`/`listOrVideoModels`), surfaced in the Settings routes table.
- Why (verified): `validateRoute` (modelRoutes.ts:64-78) validates local candidates against a passed shelf but NOTHING validates a stored cloud model against the live catalog — `resolveRoute` returns stored routes as-is, so a model delisted by the provider resolves silently into a dead RUN at spend time (or render time). The picker's honest loading/error/empty states cover browsing, not stored state.
- How: new pure function beside `validateRoute` (same file, same style); the settings console calls it after catalogs load; the route row shows the warning with a CHANGE affordance that already exists.

**Cloud `llm` generation type** — Value Med · Effort M
- What: flip `cloudRunnable: false` on the `llm` type and wire a text generation screen through the OpenRouter chat transport the optimizer already rides.
- Why: the type vocabulary and routing exist; the flag comment says "the picker never offers a route the engine can't run" — the engine (chat transport, `openRouterChat`) exists in-repo but no generation screen consumes it. A user wanting a one-off text generation (lyrics draft, prompt rewrite) has no seat.
- How: schema-driven text output pane (the CloudPane mapping already renders every published input; text output is one more mapping), route row for `llm` in settings. Product call first — the brain console overlaps this need.

## Nice-to-haves

- Human labels on stored routes (`Route.label?`) — the routes table shows opaque `service/slug` strings; a user-named route ("cheap video drafts") would read better. Low.
