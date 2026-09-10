<!-- colibri review
source: src/surfaces/OutputsSurface.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 0b4e589086fd1b315c376bb8664ed673f251f4183d0e25ca74aee3dd90db099d
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable. The lens filters both divisions with named empty states and a live-match placeholder; SHOW IN LIBRARY opens the library scoped via the same store setters the rail uses (surface switch + open + folder). Case sensitivity folded with toLowerCase on both sides.

- REFUTED in pass 3: "typing into the lens could break the film reproduction flow" - the lens only filters render lists; reproduceFilm reads the unfiltered film objects.
