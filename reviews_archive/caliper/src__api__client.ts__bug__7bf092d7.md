# colibri bug review - src/api/client.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 7bf092d7 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- [MEDIUM] freeVram never checks res.ok - a failing /free (the proxy-404 class of bug that already happened once) resolves cleanly, callers report unloaded while the server keeps every model. Fix: throw on !res.ok.
- [LOW] cancelQueued/interrupt share the same pattern; acceptable (ws events reconcile state) but freeVram is the one whose lie surfaces in UI.
