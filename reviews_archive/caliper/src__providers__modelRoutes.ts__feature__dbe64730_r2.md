# Colibri review — src/providers/modelRoutes.ts (feature, run 2)

- **Source:** `src/providers/modelRoutes.ts` · **sha256:** dbe64730 (bytes identical to run 1 — doctrine pass 2 loads run 1 as context; run 1's artifact stands)
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature, pass 2
- **Context pack:** 5 importers (api/catalog, api/modelRoutes, DeckControls, vite.routes); E-2 shipped the catalog-side GONE flag for retired cloud picks (run 1's stale-route High, satisfied at the catalog layer); outline + run-1 artifact as base.

## What this module does (unchanged bytes — run 1 has the full map)

The universal routing core: five GenTypes with shelf/category/runnability, Route/RoutesConfig, shelf-aware validateRoute, local-first resolveRoute, and the profile gate.

## Run-1 add-on status

- Stale-route detection → SHIPPED at the catalog layer (E-2: retired cloud picks say GONE FROM CATALOG in the picker).
- Cloud llm generation type → still open (rests in run 1; product call — the brain console overlaps).
- Route human labels → open, Low (run 1).

## Suggested add-ons (NEW this pass)

**Price basis on the route row — routing as a money decision** — Value Med · Effort S-M
- What: the Settings routes table (and DeckControls' route hints) show each stored route's live price basis — $/image, $/second, or $/run from the same price pipeline the ladder uses (orPriceSummary, replicatePriceInfo).
- Why: a route is a standing money decision the owner makes once and forgets; the catalog side speaks prices everywhere (cost-on-the-button is house law), but the ROUTES table shows a bare service/slug string with no cost. Switching the video route from an 8¢/s engine to a 30¢/s one is invisible at the moment of the switch.
- How: the routes console already fetches catalogs (E-2's GONE check rides the same load); join the price blob per slug; one column. Pure display over existing data.

**Route health memory — "last worked" per stored route** — Value Low-Med · Effort M
- What: a tiny persisted per-route record (last success timestamp, last failure + message) written by the run paths; the routes table shows it.
- Why: key liveness answers "is the KEY alive"; nothing answers "does THIS ROUTE still run" — a model that started erroring every run (schema drift upstream, a renamed input) looks identical to a healthy route until the next spend fails. The owner's stagnant-route instinct (E-2) deserves run-level evidence.
- How: a small JSON beside model-routes.json; runOrVideo/runPrediction/eachlabs call sites write one line on completion/failure; the table renders it. No gate, no behavior change — memory, not judgment.

**Route presets (mass flip)** — Value Low · Effort S-M
- What: named route-table snapshots ("rehearsal routes" / "finish routes") the settings console saves and restores in one click.
- Why: the film flow owns its engine pairs, but the one-off Generate pane owns these routes; a deliberate session shape (all-cheap exploration vs quality one-offs) currently means re-picking five routes by hand.
- How: RoutesConfig is already a small JSON; snapshot/restore mirrors the graph backup pattern (listGraphBackups/restoreGraphBackup exist client-side as the idiom).

## Nice-to-haves

- Route human labels (run 1's Low) — pairs naturally with the price column above.
