# colibri bug review - src/components/ScrubInput.tsx

reviewer: ZCode (GLM-5.3, in-session) - sha256 c985b952 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - pointer-captured scrub, settle-clamp-snap pipeline, typed-then-blur commit discarding NaN, pinned mode fully inert.
