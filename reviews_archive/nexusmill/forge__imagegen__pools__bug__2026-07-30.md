# Colibri review — image generation across Forge, Library and programmatic paths

- **Date** 2026-07-30 · **Mode** bug + Phase D debug · **Reviewer** in-session (Claude Opus 4.6)
- **Units** `forge/imagegen/prompts.py`, `forge/library_gen.py`, `forge/imagegen/replicate_flux.py`,
  `forge/bundle.py`, `forge/quality.py` (new)
- **Context pack** CLAUDE.md canon (G2 no-guessing, G13/G14 security, AF-TWIN parity);
  `docs/remediation_manifest.json` (191 entries — prior fixes excluded up front);
  `docs/deferred_manifest.json`; commits `302a521`, `91fb565`, `c56e610`; the 48-image
  STYLE_PICK reference set with Damien's 17 annotations as ground truth.

## Verdict

Shippable. The generation pipeline's *mechanism* bugs are now closed; the remaining quality gap
is prompt CONTENT, which is editorial, not structural. The single biggest risk is that this gap
keeps getting misdiagnosed as a code bug — this review's main contribution is proving, with
measurements, that it is not.

## Phase D — the failure Damien circled

**Signal.** 17 of 48 images marked bad. Because subject and seeds were held constant, assignment
position fixes palette/composition/finish, so the marks implicate those axes rather than style.

| pos | palette | composition | lum | spread | detail | circled |
|-----|---------|-------------|-----|--------|--------|---------|
| 1 | sapphire and amethyst | subtly irregular natural | 68 | 115 | 11.2 | 2/12 |
| 2 | ivory and charcoal | macro close-up | 148 | 249 | 27.3 | **0/12** |
| 3 | burgundy and cream | **fine-scale intricate repeat** | 128 | 195 | 24.5 | **9/12** |
| 4 | blackened steel and ember | crisp fresh pristine | 39 | 90 | 12.4 | 6/12 |

**Hypothesis ledger.**

1. *Position 3 is lacy because of `fine-scale intricate repeat`.* → **CONFIRMED, already fixed.**
   STYLE_PICK predates `c56e610`. Verified against current code: 0 banned-composition hits across
   102 assignments for `dragon skin`. Accounts for 9 of the 17 marks.
2. *Position 4 is bad because dark-dominant palettes kill tonal range.* → **REFUTED. Deleted.**
   See below. This was my leading hypothesis and the data killed it.
3. *A metric floor can catch "bad" generally.* → **REFUTED.**

## REFUTED finding, recorded so it is not re-attempted

I built a quality gate on the premise that darkness/flatness predicts badness, with thresholds
from per-position group means. Checking it against the annotations refuted it:

| metric | lowest **kept** | lowest **circled** |
|--------|-----------------|--------------------|
| spread | 45.0 | 66.0 |
| luminance | 25.5 | 32.9 |
| detail | 5.6 | 8.8 |

The darkest, flattest, least-detailed images in the set are ones Damien **kept**; everything he
rejected scores **better** on all three. A sweep from 20 to 135 found no threshold with zero
false positives that caught any meaningful share of the marks. Aesthetic quality here is
**subject legibility**, a prompt-side property not recoverable from image statistics.

`forge/quality.py` was consequently rewritten to sit strictly *below* the worst accepted image.
It now guards only against degenerate output — all-black, blown-out, structureless gradient,
i.e. what a collapsed generation or provider failure looks like. It rejects 0 of the 48 and is
documented as explicitly not a taste oracle.

## Findings

**[MEDIUM] `LIBRARY_FINISHES` holds only 6 entries** — `prompts.py`
- What: the relief axis, which is the entire point of a height-map library, offers 6 phrasings
  (5 after the organic filter).
- Trigger: any request with n > 6 per type.
- Impact: silent repetition on the axis that most determines whether a texture is worth having.
- Fix: expand to ~16, covering bevel profile, edge sharpness, wear state and shoulder geometry.
- Status: **CONFIRMED** (measured directly). Not fixed here — it is content authoring.

**[LOW] Cross-axis scan is otherwise clean** — `prompts.py`
- Four flags, all false positives on inspection: `ornate filigree border frame` and
  `badge / seal medallion` live in `COMPOSITIONS`, the *emblem* pool, where ornament is correct;
  `gold-foil accents` is an emblem finish. `precisely machined relief` is already gated by
  COMPOSITION-1. **No new contamination.** The scan is retained as a standing gate — this bug
  class has now appeared four times.

**[INFO] The four historical content bugs share one root cause.** Materials in the palette slot
(wood grain), emblem moods in texture prompts (medallions), geometric layout on organic subjects
(brickwork), ornament style presets (florals). Each was a pool written for one axis being drawn
for another. `audit_pools.py` now enumerates every pool against its permitted axes.

## Missing safeguards

- No standing check that pool sizes exceed the largest realistic `n` (would have caught the
  6-entry finish pool).
- `audit_pools.py` and the preflight gates live in `junk/` and are not in the feature harness.
- No per-type quality record, so a type that reliably produces poor output is only found by eye.

## Verification

`test_composition.py` 7/7 · `test_quality.py` 11/11 · `test_palette.py` 7/7 ·
`test_cdn_host.py` 13/13 · `test_concurrency.py` 17/17 · `test_parse_preamble.py` 6/6.
Every finding above was re-traced against current on-disk bytes; two were refuted and deleted.
