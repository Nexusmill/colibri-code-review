# colibri bug review - src/film/produce.ts (delta)

source: src/film/produce.ts · reviewer: ZCode GLM-5.3 in-session · sha256 d90075d8513bd8a8e04b9c3cadb3cf61c18f2d8601386ae7c4cf4e6d03aecbb3 · 2026-09-05 · mode: bug (delta vs 8f9b4362 @ 9fbf2e8 2026-08-24)
context: full current file read (89 lines); delta 49+3 = the keyframe-gate planning + checkpointBoundary; cross-file: runProduce's use of both (vite.film.ts e827383d review), produce.test.ts fixtures (boardApproved set explicitly), boardApproved writers repo-wide.

## Verdict

Shippable - internally consistent and the gate math is right. One cross-file trap (filed on vite.film.ts): classic films with no autopilot record can never earn a segment step because nothing outside autopilot-adjust ever sets boardApproved.

## Bugs & vulnerabilities

None new in-file. Cross-file MEDIUM: segments filter `!!s.boardApproved` (line 34) combined with the writer set means the classic `create`→`produce` route pair cannot complete (see vite.film.ts__bug__e827383d for the full trace; kfReviewNow's readAutopilot ENOENT crashes multi-window classic runs first).

## Missing safeguards

- checkpointBoundary uses `film.shots[...]` spans from the run's opening read; a mid-run retime after the boundary is computed leaves the checkpoint's `seconds` label stale (cosmetic - the comment documents the intent).

## Fixed since last review

(prior 8f9b4362 had no open findings - this row's closure: none were open.)

## Verified-correct (adversarial passes, findings deleted)

- "A board that renders this pass cannot shoot this pass": segments-before-keyframes ordering + the approved-only filter means a same-pass board→segment leak is impossible (steps are fixed at plan time; rerendered boards clear approval via clearBoardVerdict).
- checkpointBoundary: only-a-checkpoint-when-more-work-follows (`i < length-1`) traced for the final-window shoot-through; -1 when one window fits; skipped.segments counts footage-on-disk not approvals (comment matches code).
- ProducePlan counts/skipped arithmetic consistent with the filters.
