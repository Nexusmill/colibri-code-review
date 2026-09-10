# colibri bug review - src/surfaces/OutputsSurface.tsx (delta)

source: src/surfaces/OutputsSurface.tsx · reviewer: ZCode GLM-5.3 in-session · sha256 ba7219d0 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs f4d4962f @ d85f4ac 2026-08-25)
context: diff ~130 lines; prior review f4d4962f carried; rulings 27/36/40; screenStore openAsset(reveal).

## Verdict

Shippable - class rename, the press-carries-you reveal on every OPEN, and the one-off shelf split with type-based ownership truth.

## Bugs & vulnerabilities

None new. The shelf filter keys on outputs type === "film" (not the film list), so a failed/slow filmList() cannot leak film-owned records onto the shelf; filmList errors now surface (filmError) instead of vanishing; text class classified before audio in cells.

## Missing safeguards

- none new.

## Fixed since last review

- (prior had no open confirmed findings)

## Verified-correct

- KIND_OF maps every class (no slice(0,-1) string surgery on labels); dedupe ring preserved; reveal=true on both film-file and model-card opens.
