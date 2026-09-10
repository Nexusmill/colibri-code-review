# colibri bug review - src/components/StatusFooter.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 64a42466 - 2026-08-19T07:55:05
mode: bug - context: full-session repo knowledge (call sites traced by read; stores/surfaces/api cross-checked)

## Verdict

Shippable. Findings below survived the adversarial pass; refuted drafts were deleted.

## Bugs & vulnerabilities

- No findings. onPurge's post-purge 4.5s cache-wait traced against the custom node's 4s counter cache.
