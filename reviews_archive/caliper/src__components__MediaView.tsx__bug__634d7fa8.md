# colibri bug review - src/components/MediaView.tsx (delta)

source: src/components/MediaView.tsx · reviewer: ZCode GLM-5.3 in-session · sha256 634d7fa8 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs ad840b10 @ d70c277 2026-08-16)
context: diff 44+2; prior review ad840b10 carried; DocView (e1f8a0be family, cache-hit) consumers.

## Verdict

Shippable - words-as-media (text documents render through DocView with film-folder image resolution) and the audio waveform plate.

## Bugs & vulnerabilities

None new. The doc fetch is alive-guarded and keyed on filename+subfolder (stale doc cannot land after a window re-targets); failure degrades to the reading placeholder forever (a corrupt doc shows "reading the words…" - minor, bounded).

## Missing safeguards

- The fetch error path sets doc=null which renders the same "reading" text - indistinguishable from slow; acceptable for local serving.

## Fixed since last review

- (prior had no open findings)
