# Colibri review — src/surfaces/BundlesSurface.tsx (feature)

- **Source:** `src/surfaces/BundlesSurface.tsx` · **sha256:** 962baf95
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the editor + install column; FEATURES.md `bundles-editor`, `install-catalog`; the app's arm-then-confirm delete idiom (library-delete, film-run-delete); R1's bundle export/import add-on (UI home); verified absence: remove is single-press, no duplicate action; last touch 82ff326 (2026-08-31).

## What this module does

The bundle table with the Files column (per-row install state: live bytes while downloading, inline HF-token ask on gated failures, installed/manual honesty), the curated Add-model modal (render bundles whose full config arrives predetermined, llama.cpp GGUFs as plain downloads, manual-file disclosure, the always-present HF token row), the custom-bundle editor modal (AdvancedDrawer with surfaced validation issues), remove, and refused-add surfacing at the rail (the every-press-visible rule).

## Suggested add-ons

**Arm-then-confirm on bundle remove** — Value Med · Effort S
- What: `remove(b)` (lines 79-81) rewrites bundles.json on a single press with no confirm — the app's own destructive idiom everywhere else is the two-press pair (library DELETE→CONFIRM, run DELETE→CONFIRM) with the consequence in the title.
- Why: an accidental click in a row of small text links ("edit | remove") silently drops a tuned bundle from the file (params/prompts for it orphan in localStorage). The pair costs nothing and matches the established pattern exactly.

**Duplicate bundle action** — Value Med · Effort S
- What: "copy" beside edit — `structuredClone(b)` through the editor with a fresh name/id (withIds uniqueness), opening the modal pre-filled.
- Why: tuning variants (same engine, different defaults/negative) is the natural workflow; today it's hand-re-entering every field in a custom bundle. Verified absent (edit/remove/catalog-add only).

**Bundle export/import row** — the UI home for the R1 schema.ts add-on (export one row as JSON; import validated by validateBundles + merged via withIds). Verified absent here (round-1 search).

## Nice-to-haves

- A disk-size column per bundle (the Files column knows presence; sizes would inform uninstall decisions). Low.
