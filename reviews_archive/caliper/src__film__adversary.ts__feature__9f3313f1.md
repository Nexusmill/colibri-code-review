# Colibri review — src/film/adversary.ts (feature)

- **Source:** `src/film/adversary.ts` · **sha256:** 9f3313f1
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the deterministic four-family judge (owner 2026-08-27, extended through 2026-09-05); the rubric lives in knowledge/film-adversary.md; called at draft, re-draft, AND window-redraft (the F-refuses-redraft doctrine); the anchor-strip fail-open fixes (2026-09-03); last touch c9bb3bb (2026-09-05).

## What this module does

The plan's judge, all mechanically decidable: STORY (anchor-stripped endpoint jaccard — a last shot repeating the first is F; middle-beat restating), CONTINUITY (anchor ≥20 chars; every prompt must carry ≥60% of its significant tokens; misses named per shot), UNIQUENESS (anchor-stripped pairwise actions at ≥0.85 jaccard = F "the run would buy the same shot twice"; board-vs-shoot restatement = craft C), TRANSITION (the cutIn canon, all-hard = C, dissolve-majority = C), CRAFT (the cram rule and size-variety and director-shorthand judged on anchor-stripped ACTION — the fail-open fixes; camera/timing token gates; the pair-capped clip ceiling), DISCIPLINE (micro-film protocol, coverage arithmetic ±34%, speech-rate on SPOKEN lines only). `adversaryCorrection` folds findings into the re-draft ask.

## Suggested add-ons

**A physics-plausibility check** — Value Med · Effort S
- What: a verb-list scan of anchor-stripped shootPrompt actions for contact-collision asks (catch, grab, collide, impact, crash, tackle…) → a craft C with the manifesto's restage note ("no catching falling objects, no body collisions — restage around contact or hide it in framing").
- Why (verified): the critique gate judges renderability at the USER prompt level (buildCritiquePrompt names the 29.5/100 physics law), but the STORYBOARD judge never re-checks — the brain can draft a collision into shot 7 after the user's prompt passed critique. The manifesto clause is mechanically pre-decidable the same way the camera-token gate is; the corpus records the class (The Super Man's static figures).
- How: one more block beside the shorthand check; the token lists pattern (CAMERA_TOKENS) is established.

**Thresholds as exported data** — Value Low · Effort S
- The jaccard literals (0.72/0.55/0.85/0.6/0.34) are the judge's tuning surface; an exported THRESHOLDS object lets tests import them and the knowledge rubric document the actual numbers (checkable, never mystical — the tiers.ts doctrine).

## Nice-to-haves

- Findings could carry the shot indexes as data (some embed them in prose) — lets the wizard highlight the offending cards. Small, pairs with the inspector.
