# colibri bug review - src/providers/catalog.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 8be04c82 - 2026-08-27
mode: bug - context: forRole/overlayChoice/spendTotal traced from vite.film's resolveScoreEntry and scoreFilm; OWNER_PRICES (owner briefing 2026-08-23) is the verified truth

## Verdict

Shippable after the one fix below.

## Fixed since this review (same session)

- [MEDIUM-LOW] The catalog's minimax/music-2.6 costUsd said 0.15 while the owner-verified price (OWNER_PRICES, same repo) is 0.013 - scoreFilm tallies the default-path spend from this constant, inflating every scored film's recorded cost ~11.5x, and the catalog display disagreed with the ladder's billing. FIX: 0.013 with a comment tying it to the owner briefing.

## Verified-correct

- forRole's throw; overlayChoice's own-price rule (null when unpublished, default's price only for the default itself); spendTotal.

## Correction (2026-08-27, owner direction)

The fix above INVERTED the truth and has been reverted. $0.15 is the page's RATE CARD price ($0.15/output audio file, machine-verified in replicate-price-cache.json) - the price budgets, bills, and spend quote per the owner's 2026-08-24 ruling that medians underprice. The ≈$0.013 figure is the run MEDIAN (one real 2026-08-23 run did bill ≈$0.013, which is why the median masqueraded as verification). The catalog carries 0.15 again; OWNER_PRICES was corrected to the rate the same day. The reviewer's claim "the old 0.15 tallied 11x the real cost" was backwards - 0.013 underquotes ~11x.
