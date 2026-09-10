# colibri bug review - src/providers/replicateBrowser.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 c800ee9f - 2026-08-27
mode: bug - context: full-sweep round five; the owner's 2026-08-24 price rulings traced through

## Verdict

Clean - rate-card-first scraper with output-metric selection (input/compute skipped), median-vs-rate distinction carried in PriceInfo, dedupe+extras collection mapping, magic-byte extension sniffing, findImageInput's single-or-named rule.
