<!-- colibri review
source: vite.film.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: c698195211073f4b423234b7361630cb8ef48d7c0b0a4872d18ec5002499bac4
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable. Delta: the local recycleToBin became a thin wrapper over the shared module (two call sites unchanged); the import is the only other line.
