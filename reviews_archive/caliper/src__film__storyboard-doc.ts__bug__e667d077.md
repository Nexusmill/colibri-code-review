# colibri bug review - src/film/storyboard-doc.ts (delta)

source: src/film/storyboard-doc.ts · reviewer: ZCode GLM-5.3 in-session · sha256 e667d077 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 6911fc76 @ b3b3578 2026-08-27)
context: diff 23+11; prior review 6911fc76 (2026-09-03) carried.

## Verdict

Shippable - the delta is the newline-forgery fix.

## Bugs & vulnerabilities

None new. one() collapses embedded newlines in every brain-authored field (a dialogue containing "\n## x" once forged a panel heading in the owner's approval artifact); the multi-line compiled anchor renders as a labeled list instead of raw splicing; joinArrow/canon unchanged.

## Missing safeguards

- one() does not escape markdown emphasis characters - cosmetic only (approval doc, not machine-read).

## Fixed since last review

- (the 2026-09-03 finding this delta fixes is the embedded-newline forgery; verified present in current bytes.)

## Verified-correct

- Anchor-empty branch renders the (none) line; every interpolated field passes through one().
