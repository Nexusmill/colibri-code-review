# Colibri review — src/film/autopilot.ts (feature)

- **Source:** `src/film/autopilot.ts` · **sha256:** ada229eb
- **Reviewer:** ZCode (GLM-5.3, in-session) · **Date:** 2026-09-14 · **Mode:** feature (DELTA vs 15ed117c @ 2026-09-05)
- **Context pack:** the film autopilot's pure core (11 importers of buildDraftPrompt; vite.film imports it wholesale); deltas since last review = f921506 (PriceSource + BillLine.source), 500ad7e (ENERGY_PACING + pacedGrid + battery), 15a2ceb/5c109bc (TWO-TIER doctrine + h3-max card + measured-flag honesty); owner rulings 39-46; full read of the changed regions + winRatesFromRuns body.

## What this module does

The autopilot's brain-side contract in 889 pure lines: the AutopilotRecord and its PATCHABLE shape-guarded patch, sanitizeDefaults, validateStoryboard (timings from the grid), the ceil-carved shotGrid PLUS the energy-aware `pacedGrid` (quiet holds, peak cuts fast, 20k-take refusal), the manifesto-riding draft/redraft/world/critique prompt builders with strict parsers, and — since today — the TWO-TIER engine doctrine (CHEAP p-video→h3-max, EXPENSIVE h3-max→h3, sora retired) with `deriveEngineCards` merging the owner trio's measured prose with the live keyed shelf at each engine's own price basis, `maxClipSeconds` as the min-of-pair ceiling, and BillLine now carrying `source?: PriceSource` (owner/page/estimate) so APPROVE SPEND is never a mystery number.

## Fixed since last review

- Price provenance on bill lines (2026-09-05 High) → BUILT (f921506): PriceSource type, ladder entries, BillLine.source, rendered at THE BILL.
- Derive ENGINE_CARDS from the live ladder (Med-High) → BUILT (2026-09-05): deriveEngineCards + measured-flag honesty extended today (5c109bc).
- Energy arc computed-then-ignored (R3 finding) → BUILT: pacedGrid wired at vite.film.ts:1824 for song films.

## Suggested add-ons

**Last-frame conditioning into the film flow** — Value High · Effort M
- What: when a shoot engine lists `last_frame` (h3-max does — it is in the doctrine now), the segment call sends the NEXT shot's approved board as the ending frame.
- Why (verified): openrouterVideo.ts:93-96 still filters `last_frame` into frameImages but synthesizes only `first_frame` — the capability arrives from the shelf and dies at the schema (the R3 finding). h3-max sits in BOTH tiers and its card's first-listed strength is exactly this ("the continuity tool between takes"); the board chain already provides the material (each shot's boardPrompt is the first frame of its motion — the next board is a designed bookend).
- How: synthesize an `end_image` property when last_frame is listed; vite.film's OR i2v branch (frame_images, first_frame) adds a second frame_images entry; gated on the next board existing and being approved (never spend a frame the owner hasn't seen).

**Win-rate sample-size honesty** — Value Med · Effort S (CARRIED, one line from done)
- What: return `{avg, n}` from winRatesFromRuns and shrink toward price ordering until n≥3.
- Why (verified today): the function NOW tracks `{total, n}` internally (autopilot.ts:740-757) and then throws `n` away on the return line — a single 5★ run still outranks a ten-run 4.6★ engine in `best`.
- How: return the pair; winOf in resolveLadder applies the threshold. Tests exist for the ladder shape.

**A finish-resolution pick when the finisher publishes tiers** — Value Med-High · Effort M
- What: when the finish engine publishes multiple resolutions (h3: 768P and 2K at $0.13/s), THE ENGINES offers the finish resolution and the produce call pins it.
- Why (verified): the doctrine's own EXPENSIVE note now advertises "$0.13/s at 2K" — but the Replicate segment leg sends no resolution key (gate-reviewer finding, pre-existing), so the 2K finish is prose-only. This is also the research-backed answer to upscaling (render at 2K instead of paying to invent detail afterward).
- How: engine card gains `tiers?`; a small picker under FINISH MODEL when present; the replicate genSegment branch sends resolution (the OR branch already snaps to published enums since today).

**Strategy hint under EXPENSIVE** — Value Med · Effort S
- What: when EXPENSIVE is picked, the suggested-strategy line says the truth about money: h3-max rehearses at the same $0.08/s the finish costs — DRAFT-FIRST no longer saves money there, it buys an audition; STRAIGHT TO FINISH is the economical shape.
- Why: the two-tier collapse erased the cheap-rehearsal gap in the EXPENSIVE pair (both seats 8¢/s at 768p); nothing on screen says so.
- How: one conditional line in FilmWizard beside the existing suggestion span; pure copy.

## Nice-to-haves

- `fitDialogue`'s 2.6 wps constant per-voice (carried, Low).
- `pacedGrid` for non-song films (script pacing by scene beats) — the energy source is song analysis only today; contrived without an energy source. Skip unless asked.
