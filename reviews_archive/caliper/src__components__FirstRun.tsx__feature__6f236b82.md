# Colibri review — src/components/FirstRun.tsx (feature)

- **Source:** `src/components/FirstRun.tsx` · **sha256:** 6f236b82
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the one-time wizard (THE MACHINE / THE PACKAGE / THE FIRST THING); FEATURES.md `first-run`; the Era-51 ladder ruling context (packages 8/15/32/64 GB); the adopt-running-job and any-exit-records-done gates (2026-09-02); verified absence: no post-install proof, no disk-space read; last touch 91620a1 (2026-09-02).

## What this module does

THE MACHINE probes through the backend's own system_stats with honest away-backend states (PROBE AGAIN; "the cloud needs no backend") and the tier verdict card (card name, never-over-displaying VRAM, tier, reason). THE PACKAGE merges the verdict's per-file install plans (live bytes, adopt-on-reopen of a running fetch, vanished-job honesty), the local brain row, cloud keys saved IN PLACE with wrong-shape replace boxes, and APPLY THE VERDICT writing the profile with the deck reading it the same session. THE FIRST THING hands off without duplication (three doors + NOT NOW). Any exit records done — StrictMode-safe, write-before-close with the failed-write stay-open.

## Suggested add-ons

**A one-frame smoke test after install** — Value Med-High · Effort S-M
- What: when a package reaches INSTALLED, offer "RENDER ONE FRAME" — a fixed-seed, smallest-shape bench render through the just-installed bundle, result shown inline (image or the server's error verbatim).
- Why (verified): the wizard moves multi-GB engines onto disk and the first proof of life is left to the user elsewhere; the tier ladder's whole premise (this package at this VRAM) is a claim no click ever tests. Pairs with the R1 post-install size/hash verification (bytes-on-disk ≠ loads-and-renders).
- How: the bench machinery exists (vite.bench fixed-seed A/B); one row button + result chip.

**Disk-space pre-check on THE PACKAGE** — Value Med · Effort M
- The Wan-fp16-class packages are tens of GB; no free-space read precedes INSTALL. A per-plan "needs ~34 GB · 61 GB free on E:" line (server-side stat) turns a mid-download failure into an informed choice.

## Nice-to-haves

- THE FIRST THING could remember the door not taken ("you picked LOCAL last time — the cloud doors remain one key away") on re-runs. Low.
