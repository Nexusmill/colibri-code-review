# Colibri review — vite.comfy.ts (feature)

- **Source:** `vite.comfy.ts` · **sha256:** 8df4e10c
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the one naming of the ComfyUI neighbor; Era-51 config portability (the non-nvidia-mac deferral); KNOWN OPEN ITEM: the silent config-parse fallback sits on the BUGHUNT22 residual shelf (this review references it, does not claim discovery); consumed by nearly every vite.* module; last touch 91620a1 (2026-09-02).

## What this module does

25 lines: COMFY_URL and COMFY_DIR resolved from caliper.config.json (gitignored, machine-local) with this machine's values as defaults — so a cloud-only box or a different install root edits config, never code. The deliberate portability seam for the Mac deferral.

## Suggested add-ons

**Surface a malformed config instead of silently defaulting** — Value Med · Effort S
- What: on a parse failure, log the failure AND expose it (a `configError` export consumed by the status/caliper routes so the footer or settings can say "caliper.config.json is malformed — using this machine's defaults").
- Why: the catch returns `{}` silently (line 18-19); a config with a typo in comfyDir points every model path, graph seed, and power route at a wrong directory with zero indication anywhere. Already identified on the residual shelf; the feature framing is the user-facing surfacing, not just a log line.

**A /api/neighbor readout** — Value Low · Effort S
- One endpoint answering the effective URL/dir + config source (file vs defaults) — the "status text must be truthful" doctrine applied to the neighbor itself; the footer's host window could carry it.

## Nice-to-haves

- Config schema validation beyond parse (unknown keys warned) — Low.
