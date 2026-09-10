<!-- colibri review
source: vite.recycle.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: d6a05a8afa67eae1b309d4592755e10146fc567caf13d82b43bedfb730aa16f6
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable. Verbatim lift of vite.film.ts's recycle machinery (queue file, serialized chain, pinned cwd, kill timer) - the security posture travels with it: no run data in argv/env, the ps1 reads the fixed queue file.
