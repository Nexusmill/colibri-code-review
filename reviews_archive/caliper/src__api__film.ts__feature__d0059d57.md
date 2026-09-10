# Colibri review — src/api/film.ts (feature)

- **Source:** `src/api/film.ts` · **sha256:** d0059d57
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the film client — every wizard action flows through it; the 11 retired classic wrappers were removed in Era 53 (verified clean); last touch c9bb3bb (2026-09-05).

## What this module does

The typed client for the film engine: one `post()` with error unwrapping, the film/artifacts UI types (FilmArtifactsUi's eight classes mirroring readArtifacts), the runs-manager summary type (stage truth fields: busy/verdict/halted/deleteError), the ~20 autopilot actions (create/patch/draft/bill/approve/run/status/rate/upscale/adjust/delete, the checkpoint verdicts, the finishing switch, ref attach, song upload, ladder, defaults), AutopilotJob, GradeBook with the keyframe-review verdict flags, and LadderResponse.

## Suggested add-ons

**A call timeout family** — Value Low · Effort S
- `post()` has no timeout (browser default); every action is documented as blocking by design, but a hung middleware (server dead mid-request) leaves the wizard's busy states stuck until the browser gives up. An AbortSignal.timeout per action class (fast for patch/status, generous for draft/bill) would turn hangs into the error strip's honest failures.

**Plan-preview action** — cross-ref the produce.ts review's add-on (planProduce counts before START): the client gains `autopilotPlan(id)` when the server side lands.

## Nice-to-haves

- The repeated `import("../film/autopilot").X` return-type casts could re-export the record/job types once at top — pure tidiness.
