# colibri bug review - src/surfaces/QueueSurface.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 a679ed2b - 2026-08-27
mode: bug - context: full-sweep round five; queueStore/api client contracts traced

## Verdict

Clean - poll intervals cleaned up; the untracked-entry kill uses the server's only lever for running entries (global interrupt - one job runs at a time); honest elapsed/status rendering; recall-seed handoff.
