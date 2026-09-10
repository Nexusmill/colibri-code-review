# Colibri review — src/components/ModelPicker.tsx (feature)

- **Source:** `src/components/ModelPicker.tsx` · **sha256:** c8bdd8a9
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the universal picker + ModelScreen + the exported SchemaField mapping (shared with CloudPane); FEATURES.md `replicate-models`, `generate-cloud-pane`; one-price-pipeline doctrine (2026-08-23); verified absences: no recents, no per-model value memory; last touch a7a6aea (2026-08-25).

## What this module does

Three layers. The picker overlay (portaled to body — the clipping lesson): profile keys, local shelf (USE LOCAL / DOWNLOAD with install kick-off), cloud service select with key-gating and no-shelf honesty, searchable rows with BUDGET badges, run counts, and price truth (pending "…", none "—"). ModelScreen: any model's published inputs become a form — defaults seeded including first-enum (a required enum never dead-ends RUN), required + image inputs pinned, advanced folded, RUN with the page's own figure, SET AS DEFAULT writing the route, artifact → screen window + library, deck status-well fed (R1). SchemaField: the universal mapping — uri single/multi image pickers with previews, enum select, enum-set chips, arrays as lists, objects as live-validated JSON, numeric bounds shown.

## Suggested add-ons

**Per-model value memory** — Value Med · Effort S
- What: remember last-used values per `service/slug` (localStorage); reopening a model restores them over schema defaults.
- Why (verified): every open re-seeds from the schema (the defaults effect at lines 221-250); a user iterating on one model re-picks resolution/duration each time. Click-safe: restoring text writes nothing.
- How: persist `values` on run per slug; seed order becomes saved → default → first-enum. Apply to CloudPane too (same pattern, its own effect at CloudPane.tsx:40-58).

**Recents / pinned rows** — Value Med · Effort S
- A "recently opened" section at the top of the cloud list (per type); catalogs are long and repeat picks are the norm. Verified absent.

**Sort control on the catalog** — Value Low · Effort S
- Rows arrive in catalog order; sort by price (where priced) / run count / name. Pairs with the budget badge's intent.

## Nice-to-haves

- The search could match service hints (e.g. "openrouter" narrowing when the type spans services) — the service select already scopes; marginal.
- SchemaField's JSON objects could format on blur — QoL.
