# colibri bug review - vite.caliper.ts (delta)

source: vite.caliper.ts · reviewer: ZCode GLM-5.3 in-session · sha256 c65d6bba (full sha in manifest) · 2026-09-05 · mode: bug (delta vs d017efc9 @ a02e2b8 2026-08-23; unchanged regions byte-identical to prior-reviewed sha, delta read = diff + cited lines fresh)
context: diff 101+12; prior review d017efc9 (zero confirmed findings) carried; cross-file: vite.comfy COMFY_DIR/URL, install/tiers judgeTier, vite.keys servicePresence, the seven middleware modules whose mounts dropped the shared readBody.

## Verdict

Shippable - no new defects. The delta is the portability centralization, five new MODEL_ROOTS families, the first-run/recommend handlers, and a real concurrency fix.

## Bugs & vulnerabilities

None new in the delta. cleanGpuName's last-colon strip is cosmetic-only (device readout); handleInstallRecommend's away-backend path returns verdict=null (judgeTier nulls - no guessing) with the plans/brain merge gated on verdict presence; handleFirstRun is presence-is-done with a gitignored file. The install-start re-check AFTER readBody's await closes the 2026-08-31 gate finding (jobNow snapshot).

## Missing safeguards

- streamDownload redirect-following beyond the pre-checked host allowlist (prior note, unchanged - HF CDN is the legitimate case).
- handleInstallRecommend probes system_stats with a 2.5s timeout on EVERY call - a cold backend costs the caller 2.5s each time (bounded, acceptable).

## Fixed since last review

- (no open findings at d017efc9; the concurrency re-check fix landed in this delta)

## Verified-correct (adversarial passes, findings deleted)

- The seven middleware mounts dropping readBody: each module now owns its body reading (verified per-module in their own reviews this pass) - signature consistency traced at every mount.
- MODEL_ROOTS additions are data rows in the same shape; no new traversal surface (safeJoin path unchanged).
