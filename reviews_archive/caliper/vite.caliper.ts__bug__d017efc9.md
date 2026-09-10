# colibri bug review - vite.caliper.ts

reviewer: ZCode (GLM-5.3, in-session) - sha256 d017efc9 - 2026-08-26
mode: bug - context: the composer - every middleware mounted here; the serialized/atomicWrite machinery traced against concurrent PUTs; installer path joins against extra_model_paths layout; both configureServer AND configurePreviewServer (the desktop icon serves preview)

## Verdict

Shippable - no defects.

## Bugs & vulnerabilities

None confirmed. The per-path serialized write queue (prev.then(fn, fn) with swallowed stored rejections, caller-visible next) prevents interleaved half-writes; atomicWrite tmp-rename; graph backup prune keeps the newest 5 with full stamped-shape matching (the prefix-leak fix holds); provenance PUT shape-checks records; the installer's safeJoin + MODEL_ROOTS deny traversal; streamDownload's .part-then-rename and gated-401 reporting; the install job shares progress with the sidecar provisioner.

## Missing safeguards

- streamDownload's host allowlist is checked pre-redirect; fetch follows redirects anywhere (HF CDN redirects are the legitimate case) - same soft-boundary note as vite.llm/vite.replicate.
