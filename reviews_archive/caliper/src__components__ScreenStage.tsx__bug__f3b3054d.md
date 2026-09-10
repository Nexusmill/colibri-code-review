<!-- colibri review
source: src/components/ScreenStage.tsx
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: f3b3054de101fa7f757e0d1082c3b884d9b15f1b5ae78ac25badcd7f908aa38d
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable. The delete foot speaks the server's say (Recycle Bin, recoverable); both views' DELETE titles updated to the same truth. Films refresh-on-reopen verified true by construction (mount-gated component + mount-effect fetch) - no change made, recorded in HISTORY.
