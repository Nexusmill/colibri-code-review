# colibri bug review - src/api/ws.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 8d535ac7 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- No findings survived verification. Socket identity guards, reentrant connect, backoff reset, and stale-onclose all traced correct; parseWsMessage is total over malformed input.
