# colibri bug review - vite.routes.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 a9e1c274 - 2026-08-27
mode: bug - context: full-sweep round five; this file also served as the refutation witness for providers/modelRoutes (cloud-only wipes routes)

## Verdict

Clean - config shape-validated on read; validateRoute before every write; the cloud-only profile wipes stored routes (line 97), which is what makes resolveRoute's stored-local path unreachable.
