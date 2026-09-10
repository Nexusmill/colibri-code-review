# colibri bug review - post-fix delta bundle (remediation wave, 2026-09-05)

This file records the post-fix state of the remediation wave's OTHER touched files (one row each; the wave's full adversarial record lives in the five commit-gate rounds gate_20260905-101122 through -115032, plus tranche-1's round -102033). All fixes verified: tsc exit 0, vitest 365/365 (48 files), commits a8dfbfd + c9bb3bb through the armed gates.

## src/film/budget.ts - sha cb357275 - FIXED (HIGH strategy-blind bill)
computeBill gained the finishPass line (own tier rates, null honesty, band widening, retry-margin inclusion); 5 new tests. Gate round 1 BLOCKed the original perStep consumer (a missing line = zero estimate = ungated finish) - fixed by the caller's refusal guards; round 2 CLEAR. Open: none.

## vite.film.ts - sha af1eb46f - FIXED (classic-routes trap, done-log, queue clock, cap threading)
autopilot-bill prices the pair (strategy-aware) and ALWAYS carries the finish line for draft-first; autopilot-finish and finish-mode resumes REFUSE without a priced shoot-finish line (the zero-estimate ungated-run hole); the eight trapped classic writing actions retired with an honest 400; the done-log contradiction fixed (worked flag); queueAndWait wall-clock 15-min cap; judgeStoryboard threaded maxClipSeconds at all three sites. Gate round 2's MEDIUM (grid slop vs the 15s pair cap) fixed at the SOURCE: shotGrid now ceil-carves (autopilot.ts) so no slot exceeds the clip length. Round 4 flagged the 15-min cap's slow-render note as a deliberate trade (non-blocking). Open: none.

## src/film/autopilot.ts - sha 15ed117c - FIXED (${d}s literal, PATCHABLE shapes, ceil grid)
The micro-film protocol interpolates the real duration (test pins no ${d}); PATCH_SHAPES enforces per-section kinds (visuals string, others objects - round 1's object-guard-on-visuals HIGH fixed, test added); shotGrid ceil-carves (the 112s/15 -> 16.0s unrenderable-slot class, gate round 3's MEDIUM, test added); the 251s test updated to 51 slots. Open: none.

## src/film/adversary.ts - sha 9f3313f1 - FIXED (20s literal, single-strip)
The seconds ceiling takes opts.maxClipSeconds (default 20; message updated, existing test updated, new cap-tolerance test); actionOf strips EVERY anchor copy (echo regression test). Open: none.

## vite.agent.ts - sha c25dadcb - FIXED (concurrent-apply last-write-wins)
The apply handler serializes behind applyChain (the read-modify-write can no longer race); noop pre-check semantics unchanged; round-3 gate verified no deadlock path. Open: none.

## vite.llm.ts - sha 921fbfd2 - FIXED (double-spawn, adopter truth)
Single-flight local start: an in-flight press is AWAITED and answered with the attempt's own outcome (round 2's adopter-lie LOW fixed); exactly one res.end per path; rounds 3-5 verified the atomicity window. Open: none.

## src/api/film.ts - sha d0059d57 - CLEANED
Eleven dead classic wrappers + three orphan types removed (zero external callers, verified twice); autopilotDelete carries the queued flag. Open: none.

## src/components/FilmWizard.tsx - sha 77eb2282 - FIXED (bill retry, resume, races)
Bill pricing auto-retries once and RE-ARMS on step exit (round 1's dead-end LOW); the catch-path draft resume parses BEFORE dispatch (round 2's render-phase crash LOW); the retry's updater guards on record id (round 4's wrong-run overwrite LOW); the local-draft resume survives a failed runs list. Open: none.

## src/components/MediaView.tsx - sha 5dc0e38c - FIXED (error state)
Failed document fetches render a distinct truthful error line (design-adversary verdict A: docs/reviews/wizard-retry-docview-error-2026-09-05.md). Open: none.

## tools/ui-harness.mjs - sha be607106 - UPDATED
film-score skip text matches the run-based flow; the film-produce phase regex accepts the checkpoint phase (the gate-noted pre-existing nit). Open: none.

## comfy/caliper_vram.py - sha 6d0712f5 - FIXED (the shelved CORS + 200-zeros MEDIUMs)
Degraded counter reads answer 503 with the full body (every staged consumer parses the body unchanged; the app client throws on !ok and keeps its last good read); /caliper/power refuses cross-origin Origins (localhost hosts only; the server-side handshake carries no Origin). py_compile green; sha-synced into E:/AI/ComfyUI/custom_nodes (verified identical); ACTIVATES AT THE NEXT BACKEND START. Open: none.
