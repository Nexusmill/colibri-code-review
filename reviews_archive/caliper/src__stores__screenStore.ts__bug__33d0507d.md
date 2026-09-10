# colibri bug review - src/stores/screenStore.ts (delta)

source: src/stores/screenStore.ts · reviewer: ZCode GLM-5.3 in-session · sha256 33d0507d (full sha in manifest) · 2026-09-05 · mode: bug (delta vs dc83b754 @ 57ac85c 2026-08-25)
context: diff 15+4; prior review dc83b754 carried; rulings 33/40; consumers: OutputsSurface open presses (reveal=true), job auto-open (no reveal).

## Verdict

Shippable - words-as-media asset class, the press-carries-you reveal, and persisted maximize/restore geometry.

## Bugs & vulnerabilities

None new. reveal=true routes the user to the generate surface before opening/raising the window (a no-op when already there); machine auto-opens never reveal (a machine action never moves the human). partialize now persists libraryMax/libraryRestore (reload restores maximized state).

## Missing safeguards

- none new (existing-window path raises + unminimizes as before).

## Fixed since last review

- (the 2026-08-30 "wont let you open any of the assets" silent-open finding this fixes is the reveal itself; verified present.)

## Verified-correct

- Cross-store useUiStore.getState().setSurface avoids circular-init (zustand getState at call time); text class rides the same window machinery.
