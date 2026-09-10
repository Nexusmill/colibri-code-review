<!-- colibri review
source: tools/ui-harness.mjs
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 8914cd134c4fa3ee724b34672242e7208c12d427bb9983bcea1e001203f27803
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable after two in-pass selector fixes (the library bar speaks swin-title/swin-meta, not lib-title; the lens clears through the native setter - triple-click+Backspace raced React). export-manifest restores the fixture AND removes its own zip dir; outputs-filter/show-in-library recycle their fixtures on every exit path.
