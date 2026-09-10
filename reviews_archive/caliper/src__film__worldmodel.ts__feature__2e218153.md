# Colibri review — src/film/worldmodel.ts (feature)

- **Source:** `src/film/worldmodel.ts` · **sha256:** 2e218153
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** 4 importers (autopilot.ts takes compileAnchor; vite.film.ts takes validateWorld/withWorldAnchor; carriesAnchor imported by TESTS ONLY — verified dead-in-prod); owner rulings 42/43; FEATURES.md `film-wizard` row; last touch a0077ba (2026-09-03).

## What this module does

The typed world model — the schema's teeth for rulings 42/43: `validateWorld` strict-parses the brain's JSON into CharacterSheets (garment-by-garment wardrobe, movement signature, numbers-not-adjectives) and SetSheets (frame-left/right, per-light physics), `refuseDuplicates` enforces names-as-selection-keys, `compileAnchor` renders the frozen continuity block every prompt carries, `withWorldAnchor` injects it code-side so the brain can't garble its own constants, and `carriesAnchor` is token-coverage checkability for "future gates."

## Suggested add-ons

**A world REVIEW/EDIT gate before drafting** — Value High · Effort M
- What: after the world builds (vite.film.ts autopilot-draft's 3-attempt loop, lines 1623-1633), pause at THE PLAN with the compiled anchor rendered human-readable and an EDIT affordance: the owner corrects ("her hair is auburn not black"), one re-ask amends the world, the anchor recompiles, THEN the storyboard drafts.
- Why: characters are CONSTANTS for the run's life — a brain-mis-built constant (wrong hair, wrong height) poisons every board and every shot, and today the only repair is rejecting windows after real money spent, or hand-editing `record.world` through the raw patch surface (PATCHABLE already includes `world`, but no wizard UI names it). The checkpoint doctrine says stop before spend; the world is the cheapest place to stop.
- How: a wizard sub-step or a THE PLAN section reading `record.world` (already persisted at draft time); the edit path is `autopilot-patch` with `world` + one brain amendment call; recompile is `compileAnchor` — all pieces exist.

**Wire `carriesAnchor` as a pre-spend gate** — Value Med · Effort S-M
- What: before `genSegment`/`genKeyframe` send (vite.film.ts), assert `carriesAnchor(prompt, storyboard.anchor)`; a prompt that lost anchor coverage fails loudly (or auto-blocks with the card marked) instead of buying an off-model render.
- Why (verified): the helper's own comment says it is "the law made checkable for tests and future gates" — and it is imported by nothing in production. The redraft path's bounded-length guard fixed silent truncation, but nothing re-checks coverage at spend time for the INITIAL draft or manual prompt edits (autopilot-adjust `op:"prompt"` writes up to 600 chars with no anchor check).
- How: one call at the top of the produce loop's segment step; the function already exists with a coverage threshold parameter.

## Nice-to-haves

- `validateWorld` max-character guard — nothing bounds `characters` length; a world of 12 characters bloats every prompt past cheap-engine context windows. A soft warning at the gate would help the brain's economy.
