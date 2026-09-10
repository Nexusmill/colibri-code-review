# colibri bug review - src/providers/replicate.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 b030d0cd - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - deadline-bounded polling (10 min), total outputUrls flattening (url/array/object shapes), byte-sniffed downloads.
