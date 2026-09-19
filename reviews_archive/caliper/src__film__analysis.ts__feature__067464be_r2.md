# Colibri review — src/film/analysis.ts (feature, run 2)

- **Source:** `src/film/analysis.ts` · **sha256:** 067464be (bytes identical to run 1 — doctrine pass 2 loads run 1 as context; run 1's artifact stands)
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature, pass 2
- **Context pack:** importers api/film, film/store, vite.film, tools/analyze-song (+tests); run 1's High (energy-aware pacing) SHIPPED as autopilot's pacedGrid (Theme B) — wired at vite.film.ts:1824 for song films; the legacy shotGrid below is the remaining twin; outline + run-1 artifact as base.

## What this module does (unchanged bytes — run 1 has the full DSP map)

Pure song DSP: RMS/flux/ZCR envelopes, tempo with the log-normal prior, the snapped beat grid, novelty section detection, energy-by-ratio, analyzePcm, and the legacy beat-snapped shotGrid.

## Run-1 add-on status

- Energy-aware shot pacing → BUILT (autopilot.pacedGrid + ENERGY_PACING; quiet holds, peak cuts fast).
- Energy arc to the UI → open, needs the visual-commission exception (run 1).
- Downbeat detection, per-section BPM → open, Low (run 1).

## Suggested add-ons (NEW this pass)

**Beat-snapped carve boundaries — cuts land ON hits** — Value Med · Effort S-M
- What: pacedGrid (autopilot) carves windows by seconds; snap each carve BOUNDARY to the nearest beat (the 0.35s tolerance snap already exists in this file's legacy grid, analysis.ts:190-198) when a beat lies within tolerance.
- Why: energy pacing sets HOW LONG each window is; nothing places the CUT on the music. A boundary landing 150ms off a snare hit is visible forever in the assembled film; snapping makes every shot change land with the song — the music-video grammar the transitions corpus names ("cut on musical phrase boundaries"). The beat data already rides every song record; this is one snapping call at the carve.
- How: pass beats into the pacedGrid call site (the record's analysis carries them); reuse the snap tolerance; a boundary with no beat in tolerance keeps its computed time (never shift a cut more than the tolerance).

**A phrase grid for the join layer** — Value Med · Effort M
- What: export `phraseGrid(beats, beatsPerPhrase = 8)`: bar-multiple lattice from the beat grid, section-aligned; assembly's dissolve/cut candidates and the redraft window edges read it.
- Why: sections are structural (verse/chorus); phrases are the CUT unit inside them — the corpus's transition law declares joins "earned" and cutting on phrase boundaries; today assembly joins where window arithmetic lands, blind to the phrase the song is speaking. A phrase lattice gives the join layer the song's own punctuation.
- How: pure function here (beat count × tempo → bar seconds; section-clamped); vite.film's assemble/review-clip carving takes optional phrase boundaries. Display-free — no visual-commission needed until the UI wants to show it.

**Retire or redirect the legacy shotGrid** — Value Low · Effort S
- What: this file's shotGrid (analysis.ts:189-211) now has a twin in autopilot (shotGrid + pacedGrid, the wired one). If no live caller remains (store.ts imports from this module — PLAUSIBLE that it takes analyzePcm/types only; unverified this pass), delete the twin or make it delegate.
- Why: two grids means a future pacing fix lands in one and not the other — the exact duplication class the colibri context-check exists for. pacedGrid's energy logic should have exactly one home.
- How: trace store.ts's import; delete or delegate; tests move to the autopilot grid.

## Nice-to-haves

- Per-section BPM (run 1's Low) — pairs with the phrase grid (bar length drifts with tempo); still Low.
