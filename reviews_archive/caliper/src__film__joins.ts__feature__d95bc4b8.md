# Colibri review — src/film/joins.ts (feature)

- **Source:** `src/film/joins.ts` · **sha256:** d95bc4b8
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the Era-53 dissolve planner (2026-09-05: dissolves hold the frame instead of smearing the song); unit-tested arithmetic consumed by vite.film's assembleFilm; the transition canon (7 joins) and the doctrine that every non-dissolve is a designed hard cut; new file, first feature coverage.

## What this module does

72 pure lines: `planJoins` designs the ffmpeg chain — each cut preceding a dissolve is freeze-padded (tpad clone) by exactly the crossfade length so xfade's overlap consumes HELD frames; video xfades while audio CONCATs (the song plays its contiguous per-cut spans unbroken — no smear, no 0.4s loss per dissolve); both timelines total the exact span sum; the padded-stream operand discipline (the gate's round-4 dangling-label fix) is baked in.

## Suggested add-ons

**A join manifest in the assembly report** — Value Low-Med · Effort S
- What: assembleFilm logs one line; a small report (or a line in script.md's assembly section) naming which joins rendered as crossfades vs designed cuts — the plan's declarations vs the render's reality.
- Why: the canon is declared in prompts and only dissolves are mechanically rendered; after assembly nothing states what the editor actually did without re-reading both files. Truthful-status doctrine at the artifact level.

**Seam previews for dissolve joints** — Value Low-Med · Effort M
- A 2-second around-the-seam preview clip per dissolve, produced during assembly (the inputs are already in hand), letting the owner eyeball the hold-frame blend before watching the whole film. Pairs with the checkpoint review culture; optional per-film.

## Nice-to-haves

- Non-dissolve transitions rendering differently (smash as a flash, invisible via occlusion) is NOT proposed: the doctrine is that the join's design lives in the SHOT PROMPTS (the declared cutIn shapes the content) and every non-dissolve is a designed hard cut — verified intent, not a gap.
