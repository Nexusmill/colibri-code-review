<!-- colibri review
source: zipWriter.test.ts
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: 645971d8c989decef0daecd63cbd7ddc6eac9535d23572a6b0202fc1a4ec9243
date: 2026-09-06
mode: bug
context: E-5 wave (library recycle delete, export manifest, 4GiB guard, outputs lens, show-in-library); live through the app incl. the raw-zip manifest check
-->

## Verdict
Shippable. The two refusal shapes use length-only fakes (no 5 GiB allocation - the guard fires first); the under-limit case still builds.
