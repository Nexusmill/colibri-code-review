# Colibri review — comfy/caliper_vram.py (feature)

- **Source:** `comfy/caliper_vram.py` · **sha256:** 6d0712f5
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the custom node — canonical here, sha-synced into ComfyUI/custom_nodes (ACTIVATES AT NEXT BACKEND START for the 503+origin-guard wave); the WDDM/dwm artifact doctrine; the 2026-09-05 degraded-read fix; the sync itself is manual doctrine; last touch c9bb3bb (2026-09-05).

## What this module does

186 Python lines serving the status-truth contract: the PowerShell process table (GPU perf counters — the Task-Manager source, base64-encoded command, subprocess with kill-on-timeout so a hung Get-Counter never stacks powershells, 4-second cache stamped at COMPLETION so a slow read is never served stale, single-element-array collapse handled), ComfyUI's resident models with loaded/total bytes, the CUDA allocator's own numbers, sys.argv (the flag-truth readback), 503-on-degraded (machine-checkable, clients keep their last good read), and the origin-guarded /caliper/power stop handshake (reply first, exit half a second later; cross-origin refused).

## Suggested add-ons

**Self-identifying payload (kill the manual sync belief)** — Value Med-High · Effort S
- What: a `caliper_node` field in the payload — `{"version": N, "file_sha256": "…"}` computed from `__file__` at import — so the app can VERIFY at runtime that the installed copy matches the canonical one.
- Why (verified): canonical-vs-custom_nodes sync is a hand-maintained sha doctrine ("keep in sync" in the docstring); nothing checks it. A drifted installed node silently serves old shapes (exactly what the 503 fix raced against). One field turns the belief into a checkable fact — the footer or the agent's snapshot can compare against the repo's own hash and SAY when they diverge.
- How: hash `Path(__file__).read_bytes()` at module load; ship it on every response. The app-side check is a follow-up in StatusFooter/systemSnapshot.

**A model-unload variant of /free with a report** — Value Low-Med · Effort S
- The app's /free call is ComfyUI's own route; a caliper-owned unload that returns WHAT it evicted (the models list it saw) would let the footer's "unload models" key report by name instead of by re-reading. Nice-to-have polish on an honest path.

## Nice-to-haves

- The counter read costs ~2.5s behind a 4s cache — an optional `?fresh=1` bypass for the purge readback path; marginal.
