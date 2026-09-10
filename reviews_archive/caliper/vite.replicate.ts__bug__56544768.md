# colibri bug review - vite.replicate.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 56544768 - 2026-08-26
mode: bug - context: consumers ModelPicker/CloudPane via /api/replicate, the ladder via replicatePriceInfo, film score via readScoreChoice; price-cache lifecycle traced across enrich/refresh/schema routes; git f9c5a4d (price-truth era)

## Verdict

Shippable after the two fixes below. The scraping machinery is polite and well-bounded; both defects were cache/count honesty.

## Fixed since this review (same session)

- [MEDIUM-LOW] A transient scrape failure (timeout, 5xx) cached `price: null` with the full 7-DAY TTL while the comment claimed "cached as unknown briefly, retried next session" - one hiccup read as "publishes no price" for a week, demoting engines in the ladder (unpriced sorts last) and blanking price columns. FIX: failures are marked `failed: true` and expire on a 15-minute clock; genuine publish-no-price pages keep the weekly TTL. The persisted cache shape is backward compatible.
- [LOW] refreshReplicatePrices' `refreshed` count doubled on the first-ever run (size - 0 + size) and reported 0 when stale entries re-scraped (size unchanged). FIX: it counts actual scrape calls.

## Verified-correct (adversarial passes, findings deleted)

- SAFE_SLUG clamps on every slug-taking route; the /run artifact path (derived filmId regex + films/ containment); fetchModelDetail's fixed API host; enrich's single-flight guard per category; the polite 300ms gap; mergeExtras' honest re-sort.

## Missing safeguards

- The host allowlist is checked on the original URL only; fetch follows redirects anywhere (works for HF's CDN redirects, but the boundary is softer than it reads - same note as vite.llm).
