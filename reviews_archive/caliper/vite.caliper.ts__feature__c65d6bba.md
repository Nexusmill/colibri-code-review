# Colibri review — vite.caliper.ts (feature)

- **Source:** `vite.caliper.ts` · **sha256:** c65d6bba
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the API hub composing every middleware (llm/kb/agent/film/replicate/keys/routes/eachlabs/openrouter/library/power) + its own handlers; FEATURES.md `install-catalog`, `first-run`, `bundles-validation`; the song-upload ffprobe-verify doctrine in vite.film.ts; Era-51 vite.comfy config-portability precedent; last touch fe8f967 (2026-09-02).

## What this module does

The local API's assembly point and four handler families: (1) bundle + provenance files — validated PUTs, serialized atomic writes; (2) the graph seeding system — seed into ComfyUI's user library AND the boot-template slot, boot-sync mirroring, timestamped backups with a 5-deep rotation and restore; (3) the installer — per-machine MODEL_ROOTS layout, safeJoin containment, HF-only download allowlist, presence scanning, one install job at a time with re-check-after-await, first-run record (server-side one-time truth), and the recommend handler merging the GPU-probe tier verdict with install plans and the local-brain check; (4) `caliperServer()` mounting ~26 routes on both dev and preview servers, with the sidecar's downloads reporting into the shared install job.

## Suggested add-ons

**Post-install verification before "done"** — Value Med-High · Effort S-M
- What: when a download finishes, verify the artifact (expected byte size from the catalog, or a recorded hash) before setting `installJob.state = "done"`; on mismatch, delete the partial and report.
- Why: `streamDownload` renames `.part` → target on stream end with no length check (content-length may be absent, `total = 0`); a connection dropped "cleanly" mid-transfer lands a truncated multi-GB model on disk marked DONE — the failure then surfaces much later as an opaque loader error. The repo already has the doctrine: song-upload ffprobe-verifies (`ffmpeg could not read that file`) at vite.film.ts:1553 for exactly this reason.
- How: `CatalogFile`/`LLM_MODELS` carry expected bytes (LLM_MODELS already does — `bytes` field used only for display); check `fs.stat` after rename in `handleInstallStart`'s completion blocks (lines 486, 515).

**MODEL_ROOTS into the portable config** — Value Low-Med · Effort S
- What: move the per-machine `MODEL_ROOTS` map (hardcoded `E:/AI/Models/...` at lines 285-296) beside `COMFY_DIR` in the config vite.comfy.ts already reads, with the current table as defaults.
- Why: Era 51 made COMFY_DIR portable precisely because machine paths in source are the portability hole; the model layout is the same class of fact and will bite the next machine move or the Mac port (an open item).
- How: extend the existing config read/write; keep the literal table as fallback defaults.

## Nice-to-haves

- Download resume: an interrupted multi-GB fetch restarts from zero (`.part` truncated on retry). Range-resume or at least a progress-honest "restarting from 0" note. Low priority while links are fast.

## Notes

- Verified non-gap: graph backup retention already exists (`backupExisting` keeps the newest 5 per name, line 137) — a retention add-on would duplicate. The full stamped-shape `isBackupOf` regex prevents prefix-name leakage between Caliper-LTX variants.
