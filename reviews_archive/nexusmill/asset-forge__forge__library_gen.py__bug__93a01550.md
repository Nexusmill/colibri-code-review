# Colibri review — Asset Forge library generation (colour/duplication/quality-floor audit)

- **Unit:** the library-generation pipeline against the LIVE library — `asset-forge/forge/library_gen.py` (primary) with cross-file synthesis over `quality.py`, `catalog.json`, `imagegen/prompts.py`, `color_hints.json`
- **Model:** claude-fable-5 (in-session) · **Mode:** bug (Damien-directed: colour repetition, duplicates, brown/grey dominance, leather all-brown, colour-locked types)
- **Date:** 2026-08-13
- **sha256 (16):** library_gen.py `93a01550b2f67f98` · quality.py `bb07a93c14744b97` · catalog.json `441bb6d0997d131c` · prompts.py `0248b5da24afb0ae` · color_hints.json `5f348b770a203c9b`
- **Context pack:** live library `~/Documents/AssetForge/library` (250 passed / 47 types, 105 flagged); latest job manifest `.af_jobs/20260812_055729_3c8fb80615/LIBRARY.manifest.json` (**flux-2-klein-4b**, 300 items) — verbatim prompts + failure reasons extracted; measured colour census + per-type 16×16 structural correlation over all 250 passed images; remediation/deferred manifests consulted (GREY-MUSH-1, COLOUR-5/6, PROMPT-4, DOCTRINE-1, HM-EXCISE all pre-read).

## Verdict
The pipeline is functioning as coded, but three coded decisions structurally contradict the product goal of a varied library: the colour-lock (COLOUR-5) makes locked types near-identical by design AND feeds four of them to a saturation floor they can never pass; the leather catalog core hard-codes "tan"; and the spectrum-hint pool is too weak against naturally-brown subjects, yielding a 57%-brown library.

## Bugs & findings (worst first)

**[HIGH] F1 — colour-locked achromatic types are executed by the saturation floor: 48 paid images, zero survivors** — CONFIRMED
- What: `catalog.json` flags zebra/cow/dalmatian `colour_locked` with identity guards demanding "jet-black … bright white". `prompts.py` (COLOUR-5) then strips every colour clause. `quality.py` `MIN_SATURATION = 0.10` fails any such image as "grey mush". The exemption exists — `prompt_wants_colour()` / `expect_colour=False`, called at `library_gen.py:890` — but `_COLOURLESS_MARKERS` is a style-keyword list (`"monochrome"`, `"black and white"`, …) and the guard text "jet-black bands raised above bright white recessed channels" contains none of those literal substrings. So the gate rejects exactly what the prompt commanded.
- Evidence: manifest — zebra, cow, dalmatian each 12 attempts, 12 flagged, every reason `grey mush: saturation 0.0XX < 0.100`. Cobblestone (naturally grey stone, no marker in prompt) likewise 12/12 flagged at 0.057–0.098. Flagged files carry `_rNNNN` retry suffixes — the pre-excise auto-retry double-billed these impossible types.
- Impact: four whole types absent from the library; ~48+ billed generations with a 0% possible pass rate.
- Fix direction: make the exemption structural, not textual — a `colour_locked` type whose guard describes an achromatic identity passes `expect_colour=False` deterministically (or per Damien's directive, drop the hard lock — see F2).

**[HIGH] F2 — the colour-lock makes every image of a locked type the same by design** — CONFIRMED
- What: COLOUR-5 suppresses palette AND mood axes for locked types; only structure morphology varies (`structure.py` pelt cluster). Cheetah: structural correlation is actually LOW (max 0.22 — the morphology axes work) but all 6 share the identical tawny-gold/black palette, so they read as repeats. Damien: "no use in having more than one image of those types."
- Impact: locked types cap out at one useful image; multiplied slots are wasted spend.
- Fix direction (Damien's call): replace the hard lock with curated identity-preserving variant slots (the curated-leather pattern: "classic tawny", "dyed indigo hide", "bleached bone", "gilded"...) — variation WITH identity, per his max-variation standard.

**[HIGH] F3 — leather's catalog core hard-codes "tan"; the trailing spectrum hints can't override a named colour in the core** — CONFIRMED
- What: `catalog.json:374` — `"macro photograph of pebbled full-grain tan leather, …"`. All six manifest prompts open with it verbatim; the appended hints were "winter colors", "earth tones", "rustic colors", "neon colors", "soft understated colors", "romantic colors". Result: 6/6 brown (measured), even the "neon colors" slot. Violates the file's own doctrine header ("a hint never names specific hues" — the CORE names one). The curated set fixed exactly this (dyed-colour leather variants) but the library catalog core was never updated — wiring-before-data again.
- Fix direction: neutralize the core ("pebbled full-grain leather") and/or route leather through curated dye slots.

**[MEDIUM] F4 — spectrum hints are too weak against naturally-brown/grey subjects: the library is 57% brown-dominant** — CONFIRMED
- What: measured — 142/250 images brown-dominant, 25/250 grey-dominant; whole types 100% brown (leather, brick, honeycomb, rope, hammered, cheetah). Of ~70 real hints, ~18 are honestly satisfiable by brown/neutral ("earth tones", "rustic", "autumnal", "vintage", "antique", "warm neutrals", "sun-faded", "desert", "canyon", "candlelit"…), and against subjects whose default rendering is already brown (leather, wood, rope, brick, basketweave) even directional hints like "romantic colors" lose to the subject prior. GREY-MUSH-1 pruned the worst greyscale-satisfiable hints but never addressed brown-satisfiable ones.
- Fix direction: per-type hint weighting (subjects with a brown prior draw from the non-brown half of the spectrum), and/or demote the ~18 neutral hints for library mode.
- Note: `staples_hexagon` is also 3/3 grey passed + 6 flagged — grey-default subject, same family as F4/F1.

**[MEDIUM] F5 — structural near-twins within types** — CONFIRMED (measurement), design cause PLAUSIBLE
- What: pixel-level duplicates are zero (no repeated generations), but 16×16 structural correlation shows near-twin pairs: leather 0.88, studded 0.88, scale_mail 0.87, polka_dot 0.79, hexagon 0.78. Combined with shared brown palettes this produces the "still a lot of duplicates" experience. Cause is composition/structure axis pools being too small or too subtle for uniform-repeat subjects — unverified per-type without reading each pool; the palette fix (F3/F4) removes most of the perceived duplication first.

## Missing safeguards
- No post-job variety report (per-type mean-hue/sat spread) — a 6/6-brown type should be visible in the job summary, not discovered by the customer.
- No structural guarantee that a `colour_locked` achromatic type is floor-exempt (F1's class of bug can recur on any new locked type).
- The catalog has no lint against named hues in core prompts (F3 violated the doctrine silently).

## Fixed since last review
- GREY-MUSH-1's own scope (greyscale-satisfiable hints, dark-pixel saturation math) is fixed and NOT re-reported; F1/F4 are new failure classes outside its patch.
- Auto-retry double-billing: already excised (HM-EXCISE tranche); the `_rNNNN` files in flagged/ predate the excise — recorded as historical evidence only, not re-fixed.

## User-report correction (G1)
Damien said the run was "klein 9b" — every manifest on disk says **flux-2-klein-4b**; no 9b run exists in `.af_jobs/`.
