# Colibri review — vite.llm.ts (feature)

- **Source:** `vite.llm.ts` · **sha256:** 921fbfd2
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the LLM sidecar lifecycle + the brain registry switchboard: anyCloudKey priority, persisted brain pick (brain.json, key-gated), turnOnCloudBrain (the film draft's auto-on), brainGate (the routing truth every consumer reads), provisioning (github/HF allowlists, Expand-Archive via argument array, recursive exe discovery), single-flight local start, stop-on-power-off; FEATURES.md `optimizer-cloud-brain`; machine: 16 GB card shared; last touch c9bb3bb (2026-09-05).

## What this module does

Caliper-owned llama.cpp lifecycle with ComfyUI untouched: provisions the binary (two release zips) and the Qwen3-4B brain GGUF on demand with the shared install-job progress, starts llama-server with a literal argument array (ctx 16384, no webui), health-gates status honestly, and manages the brain registry: local sidecar vs OpenAI-compatible cloud brains (OpenRouter/SpaceX/Groq), the persisted user pick honored whenever its key exists, cloud starts freeing the card by killing the sidecar, and the film autopilot's ability to turn the cloud brain on without the deck.

## Suggested add-ons

**A local-brain shelf (pick which GGUF runs)** — Value Med-High · Effort M
- What: scan `models-llm/*.gguf` (plus the install catalog's LLM_MODELS shelf, which already lists installable models with bytes/urls) and let the brain picker offer each as a LOCAL choice — `llmStart` provisions-or-selects and the start command points at the chosen file.
- Why (verified): `LLM_BRAIN_FILE` is one hardcoded GGUF (line 71) while the install catalog can put OTHER brains on disk — they install and then can never run. On the 16 GB shared card a smaller local brain (or a bigger one while ComfyUI is down) is a real lever; the owner already switches brains live for cost reasons (ruling 26's user-switchable brain).
- How: `provisioned()` reports the shelf; the power start takes a file param; BRAIN_OPTIONS gains local rows (label/hint curated like the cloud ones); ctx-size per-model metadata if needed.

**Idle auto-stop for the sidecar** — Value Low-Med · Effort S
- What: after N minutes with no chat/agent/film traffic, stop llama-server (first user of the next session restarts it; the single-flight start already makes that clean).
- Why: the sidecar holds VRAM for the whole session even when the user moved on to renders; "one heavy model at a time" is the machine's law and the sidecar quietly violates it when idle. Needs a last-use heartbeat (askBrain/agent chat/draft calls) — all flow through this module's consumers.
- How: a timer on brainGate reads; stopSidecar + status says so plainly.

## Nice-to-haves

- `localStarting` single-flight adoption is correct; a status field distinguishing "starting" vs "up" for adopters exists via health — fine as is.

## Notes

- Verified non-gaps: the wmic scan retirement is documented (argv truth lives in vite.agent); download hosts are allowlisted in both this module and vite.caliper's shared streamer.
