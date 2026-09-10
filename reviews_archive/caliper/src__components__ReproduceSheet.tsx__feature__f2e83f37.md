# Colibri review — src/components/ReproduceSheet.tsx (feature)

- **Source:** `src/components/ReproduceSheet.tsx` · **sha256:** f2e83f37
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the formula sheet (model + film), z-ordered above the library; FEATURES.md `outputs-archive` (REPRODUCE is the one action); the LOCK SEED doctrine; verified absence: no constraint feedback on edits; last touch d85f4ac (2026-08-25).

## What this module does

The formula sheet as a window of the screen OS. ModelSheet: the exact bundle/prompt/negative/seed/params, all editable, with the run line speaking the cost truth (a pinned-seed local rerun costs nothing; GENERATE randomizes — LOCK SEED keys it), honest read-only when the formula's engine is gone, and RUN AGAIN through the local queue. FilmSheet: the scenario/shape/engines/idea/storyboard facts, cost-then at that day's prices, and REPRODUCE FILM seeding a new run with the old formula — the wizard remounts at THE PLAN, the bill re-prices today, APPROVE spends.

## Suggested add-ons

**Live constraint feedback on edits** — Value Med · Effort S
- What: run `violations(bundle, params, cfgOverride)` as the params edit and show the messages beside RUN AGAIN (disabled while red).
- Why (verified): the sheet imports nothing from bundles/constraints — params are free inputs, and an edit that breaks the bundle's detent/cfg rules surfaces only as the queue's refusal AFTER the press. The deck's own gate (DeckControls problems[0]) is the pattern; the sheet is the deck's edit-heavy sibling.
- How: one import + a derived list; the file already holds the bundle.

**Changed-field markers** — Value Low-Med · Effort S
- The sheet's whole value is provenance; a subtle dot on fields that differ from the formula as recorded (the pre-edit snapshot is already in `item`) keeps the "exact recipe" claim visible while editing.

**FilmSheet: seed carry for model sheets is LOCK SEED; the film side could note engine drift** — Low
- When a film's picked engine has since been denylisted (ENGINE_HEALTH) or unpriced, the sheet could say so before the wizard re-bills.

## Nice-to-haves

- Multi-output formulas (a render that produced image + video) show both in provenance; the sheet could offer OPEN on the artifact it will reproduce.
