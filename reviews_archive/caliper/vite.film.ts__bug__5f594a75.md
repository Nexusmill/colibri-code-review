# colibri bug review - vite.film.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 5f594a75 - 2026-08-25
mode: bug - context: jcodemunch outline+importers (filmRoutes wired via vite.caliper; 29 commits/30d), git log 8ec349f/8d6ad75/8508c3d (self-heal + budget-gate era), gateStep signature verified in src/film/budget.ts, resolvedRoute shape in vite.routes/modelRoutes

## Verdict

Shippable after the three fixes below. Single biggest risk was money: two paid-render paths (grader rerolls, local→cloud ladder fallback) ran without the approved budget gate - both gated now.

## Fixed since this review (same session)

- [HIGH] gradeAndReroll rerolls bypassed the budget gate - `runProduce` line ~882 call site passed no gate; the reroll loop (up to 2 paid regenerations per shot) never called gateStep, contradicting its own comment "weak assets reroll inside budget". FIX: gate+est params added; each reroll asks gateStep and tallies gate.spent.
- [HIGH] A failed LOCAL route fell back to a PAID cloud engine with no gate (film-console `produce` action starts with no GateCtx) and the finally-restore wrote `replicate/<fallback-slug>` over the local route in model-routes.json - route poisoning, contradicting 8ec349f "fallback engines never poison the route". FIX: ladder fallback guarded to `route.backend === "cloud"`; local failures log and defer to the auto-retry pass.
- [LOW] GET film artifact served every non-png as video/mp4 - score.mp3/voice_NN.mp3 got a video label. FIX: mp3/m4a/ogg→audio/mpeg, wav/flac→audio/wav, webm→video/webm.

## Missing safeguards

- queueAndWait polls forever when ComfyUI stays reachable but a job never completes (server-down propagates correctly); a wall-clock cap would surface hangs as errors.
- appendProvenance caps at 200 records with no rotation signal.

## Verified-correct (adversarial passes, findings deleted)

- Path traversal on GET ?file=: SAFE_ID + basename + resolve/startsWith containment traced.
- Gate double-counting on failed attempts (est added at fail, retry, AND step-end) is conservative-by-design per 8d6ad75.
- Segment-skip logic and the skipped-shot gradeAndReroll no-op; auto-retry regex match on assembleFilm's error text; fallback restore exactness for cloud routes.
