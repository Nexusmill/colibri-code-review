# colibri bug review - src/kb/bm25.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 927454f8 - 2026-08-27
mode: bug - context: full-sweep round five

## Verdict

Clean - standard BM25 with sane IDF, length normalization, positive-score filtering; never needs the GPU.
