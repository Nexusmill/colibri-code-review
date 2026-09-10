# colibri bug review - tools/analyze-song.mjs (delta)

source: tools/analyze-song.mjs · reviewer: ZCode GLM-5.3 in-session · sha256 36232a61 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs c2c0ca0f @ 908ddcd 2026-08-20)
context: diff 26+3; prior review c2c0ca0f (2026-09-03) carried.

## Verdict

Shippable - the decode gate: error listener attached BEFORE the drain (early spawn failures), nonzero ffmpeg exit refuses, <1s or all-silence decode refuses to write a phantom-tempo beats file; --json without a path is a loud usage error.

## Bugs & vulnerabilities

None new.

## Missing safeguards

- none new.

## Fixed since last review

- (the silent-empty-beats-file finding is this delta's fix; verified present.)
