# colibri bug review - src/api/client.ts (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 9f5e8b48 - 2026-08-25
mode: bug (delta on 7bf092d7, 2026-08-19) - context: 13 importers enumerated (queueStore, StatusFooter, GraphSurface, ScreenStage, bundlesStore...); viewUrl's film branch cross-checked against the film middleware's GET route

## Verdict

Shippable - the delta is clean.

## Fixed since last review

- [OLD MEDIUM] freeVram ignoring res.ok: FIXED - line 128 throws on !res.ok with the status, with the proxy-404 rationale in a comment.

## Still open (accepted)

- [OLD LOW] cancelQueued/interrupt remain fire-and-forget without res.ok - accepted then and now: ws events reconcile state and a failed delete self-heals on the next event.

## New findings

None confirmed. viewUrl's film branch (`/api/film?id&file`) matches the film middleware's validated GET route (SAFE_ID + basename + containment); the power endpoints surface ok/error honestly.
