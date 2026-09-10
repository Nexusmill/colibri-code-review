# colibri bug review - vite.openrouter.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 1d310b9d - 2026-08-27
mode: bug - context: round 4's vite.replicate failure-TTL fix is the sibling; runOrVideo/runOrImage traced against the provider; artifact path boundary checked

## Verdict

Shippable after the one fix below.

## Fixed since this review (same session)

- [MEDIUM-LOW] The exact defect round 4 fixed in vite.replicate: a transient scrape failure (!r.ok or throw) cached an all-null price with the full 7-DAY TTL - one hiccup read as "publishes no price" for a week on the OpenRouter shelf. FIX: failures marked and expired on a 15-minute clock; genuine no-price pages keep the weekly TTL; !r.ok now throws so failures are distinguishable at the call site.

## Verified-correct

- SAFE_MODEL_ID clamp; the async video poll (content endpoint with key - the 401-as-video lesson); image chat-completions data-URI/link handling; saveOrArtifact films/ containment + provenance; catalog TTLs; the serialized enrich queue.

## Missing safeguards

- Redirect-following vs the fixed API host (same soft-boundary note as llm/caliper/replicate).
