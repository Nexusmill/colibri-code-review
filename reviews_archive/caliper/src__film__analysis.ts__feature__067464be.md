# Colibri review — src/film/analysis.ts (feature)

- **Source:** `src/film/analysis.ts` · **sha256:** 067464be
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the song DSP (pure, synthetic-signal tested; the CLI/middleware decodes via ffmpeg); analysis rides every Film record; shotGrid here is the legacy-local grid (the autopilot grid is autopilot.shotGrid); verified: energy classes computed but shotGrid paces flat 5s; unchanged since 908ddcd (2026-08-20).

## What this module does

Pure DSP in 211 lines: centered RMS envelopes (peaks land ON events), half-wave flux, zero crossings, tempo by flux autocorrelation with a 90–150 BPM log-normal prior, the beat grid (best phase, onset-snapped, one refinement pass that kills hop-quantization drift), section detection (novelty over normalized per-second [rms, zcr, flux], 8s minimum gaps, local-max peaks), energy classified by RATIO TO THE LOUDEST SECTION (distributions unstable, ratios stable), and `analyzePcm`. The legacy `shotGrid` carves beat-snapped ~5s slots per section.

## Suggested add-ons

**Energy-aware shot pacing** — Value Med-High · Effort S-M
- What: pace the grid by the section's energy — quiet sections carve longer shots (say 7s), peak sections shorter (3s), mid at 5 — instead of the flat `targetSec = 5` (verified at analysis.ts:189-211).
- Why: the analysis already computes the energy arc (that's its most expensive output) and the grid ignores it; cutting faster in the chorus and holding in the verse is the grammar of music video itself — the song's structure becomes the film's rhythm with no brain involvement. The autopilot's `shotGrid(duration, clipSeconds)` is where the run path would consume it (the record carries analysis).
- How: a per-section target table parameterized on `Section.energy`; both grids (this legacy one and autopilot's) can share the table; the boundary snapping logic is untouched.

**Expose the energy arc to the UI** — Value Med · Effort S (display; commission for visuals)
- `film.analysis.sections` rides every record and NOTHING renders it — THE PLAN's shot rows or the run view could carry a quiet per-section energy glyph (the data is already on the wire). Filed as the data-side note; the display needs the no-visual-changes rule's exception.

**Downbeat detection** — Value Low · Effort M
- The grid snaps to the nearest beat; whether that beat is a DOWNBEAT (bar start) is unasked. Choruses usually change on bar boundaries. Marginal against the 0.35s snap tolerance; note only.

## Nice-to-haves

- A per-section BPM (tempo drift across a song is real; one global tempo stretches the grid late in long songs) — the refinement pass mitigates; Low.
