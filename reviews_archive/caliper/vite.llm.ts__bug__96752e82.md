# colibri bug review - vite.llm.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 96752e82 - 2026-08-26
mode: bug - context: sidecar lifecycle (spawn/kill, exit-null), brain switching (deck OPTIMIZE, wizard's turnOnCloudBrain), provision job sharing with the installer; the 2026-08-21 dev-server incident class in mind

## Verdict

Shippable - no confirmed defects. The lifecycle is disciplined: literal spawn args, no shell, kill on stop and on cloud switch, exit handler nulls the handle, health distinguishes process-alive from server-up.

## Missing safeguards

- The download host allowlist is checked on the original URL only; fetch follows redirects anywhere (HF LFS -> CDN hosts is the working case) - the boundary is softer than the comment reads.
- The deck's OPTIMIZE key has no pending-disable: a rapid double-click can double-spawn llama-server (second bind fails; exit-null races the shared handle). Narrow, recoverable via stop/start.
- status reports running=true for cloud brains on key presence alone - the first chat surfaces any key problem; acceptable.

## Verified-correct (adversarial passes, findings deleted)

- anyCloudKey priority chain; brainGate's running semantics per brain kind; provision's 409 single-flight and job-state terminal handling; extractServer's Expand-Archive argument array and post-extract relocate.
