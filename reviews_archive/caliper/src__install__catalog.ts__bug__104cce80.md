# colibri bug review - src/install/catalog.ts (delta)

source: src/install/catalog.ts · reviewer: ZCode GLM-5.3 in-session · sha256 104cce80 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 870cd7e2 @ 17a8e1d 2026-08-19)
context: diff 74+3; prior review 870cd7e2 carried; cross-file: MODEL_ROOTS rows added for the same five families (vite.caliper c65d6bba); tiers.ts judgeTier packages.

## Verdict

Shippable - the upper-register catalog rows plus the qwen_image_vae URL correction.

## Bugs & vulnerabilities

None new. The three stale qwen_image_vae URLs (pointing under split_files/diffusion_models/ where the file 404s) are corrected to split_files/vae/ in all three bundles; new packages are data rows (HF URLs under Comfy-Org repacks / QuantStack, manual-fetch entries for login-gated files); every new id has a MODEL_ROOTS base so installed plans route.

## Missing safeguards

- URL liveness is claim-not-verified from here (the tier ladder ruling - owner approval pending per project memory); a dead URL surfaces at install time through streamDownload's gated-401/404 reporting.

## Fixed since last review

- (prior had no open findings)

## Verified-correct

- Row shapes identical to existing entries (kind/name/url|manual); ids unique across CATALOG.
