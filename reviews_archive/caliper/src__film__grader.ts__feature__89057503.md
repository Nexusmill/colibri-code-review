# Colibri review — src/film/grader.ts (feature)

- **Source:** `src/film/grader.ts` · **sha256:** 89057503
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the self-grader's pure core (owner 2026-08-23: "grade its own output, learn from failure"); consumed by vite.film's gradeVision (gemini flash-lite→flash) and gradeAndReroll (max 2 rerolls, <3 holds the shot); unchanged since 79875ba (2026-08-24).

## What this module does

42 pure lines: `buildGradePrompt` (boards graded whole, clips as three frames start/middle/end, judged ONLY against the ask, the film's style bible, known failure patterns folded in, 1–5 with 3=usable honesty), `parseGrade` (strict: JSON-between-braces, integer 1-5, note capped at 200 chars), and `rerollPrompt` — never a blind retry: the grader's note plus the corpus's failures steer the corrected take while keeping the intent.

## Suggested add-ons

**A second opinion at the money boundary** — Value Low-Med · Effort S-M
- What: when a grade lands at 1 or 2 — the scores that trigger paid rerolls and the hold-back rule — re-ask once with the fallback grader model and keep the WORSE of the two (conservative at the spend boundary).
- Why (verified): gradeVision's model fallback fires only on parse failure, never on score; a single vision model's harsh/hallucinated 1/5 both wastes a reroll and (at <3 after rerolls) withholds a shot's footage. One extra cheap ask at the boundary only.
- How: a `confirmLow` option in gradeAndReroll's loop; the two-model pattern exists in gradeVision.

**Grade receipts into the film folder** — Value Low · Effort S
- Grades live in grades.json; appending each asset's grade+note to the film's script.md (or a grades.md artifact class) would make the corpus entry's averages checkable against per-shot truth. Pairs with the outputs-archive typed strips.

## Nice-to-haves

- buildGradePrompt could name the shot's SECONDS for clips (a 3-frame sample of a 15s take hides pacing) — the grader judges content, not duration; marginal.
