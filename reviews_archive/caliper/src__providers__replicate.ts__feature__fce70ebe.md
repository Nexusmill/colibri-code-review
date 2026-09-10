# Colibri review — src/providers/replicate.ts (feature)

- **Source:** `src/providers/replicate.ts` · **sha256:** fce70ebe
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the generic Replicate call path (predictions via the VERSION endpoint — the by-model 404 lesson, live 2026-08-27; the under-$5 6/min pacer); consumed by the film engine legs, CloudPane runs, the battery; verified: timeout throws without cancel; unchanged since e333931 (2026-08-27).

## What this module does

98 pure-fetch lines: the create-pacer (12s minimum gap serialized behind one chain — retries, fallbacks, and parallel films can never burst the rate limiter; a test seam), `api()` with honest error text, `runPrediction` (resolve latest_version, create, poll to completion with a 10-minute ceiling), `outputUrls` (recursive flatten of url/array/object shapes), and `downloadArtifact`.

## Suggested add-ons

**Cancel on timeout** — Value Med · Effort S
- What: when the 10-minute poll deadline trips (line 73), fire the prediction-cancel DELETE (POST/`/predictions/{id}/cancel`) before throwing.
- Why: a timed-out prediction keeps running provider-side and can still BILL; the throw today abandons it. The produce loop treats the throw as a failed shot and may retry — paying twice for one decision. Verified: no cancel call anywhere in the path.

**429-aware pacer extension** — Value Low-Med · Effort S
- The pacer prevents bursts proactively; a 429 response could also extend `lastCreate` reactively (back off the gap) rather than leaving recovery to callers' message-sniffing (vite.film's 65s waits). One check in `api()` on status 429.

## Nice-to-haves

- Webhook-based completion is available at Replicate but conflicts with the localhost-only network doctrine — polling is the correct posture here; not proposed.
