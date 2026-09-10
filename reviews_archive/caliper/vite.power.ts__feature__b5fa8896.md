# Colibri review — vite.power.ts (feature)

- **Source:** `vite.power.ts` · **sha256:** b5fa8896
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** the taskbar power backend; FEATURES.md `power-restart`, `power-off`; launcher/restart-comfyui.cmd + start-comfyui.cmd (flags rendered from caliper.config.json at every start); verified absence: no start action; last touch 91620a1 (2026-09-02).

## What this module does

Power lifecycle with observed states only: RESTART asks the custom node to stop, WATCHES the port down (30s ceiling, else 504 naming the stale-node suspect), spawns the detached restart tail, and polls up (150s); POWER OFF stops, watches down, kills the sidecar, exits — and on any failure stays up with the honest error. GET answers comfyUp for anyone asking.

## Suggested add-ons

**POWER ON — start the backend from the app** — Value Med-High · Effort S-M
- What: an `action: "comfy-start"` mirroring restart's tail: spawn the launcher's start-comfyui.cmd detached, poll up to ~150s, report observed truth. The taskbar key appears only when the backend is down (the footer lamp already knows).
- Why (verified): restart REFUSES when down ("start it from the launcher") — the app can cycle a running backend but cannot raise a dead one. A mid-session crash (or a backend killed by the power route's own 504 path) currently demands the desktop icon; the same detached-tail machinery that restarts can start. The flags pipeline (optimizer-applied launch flags render at every start) is preserved by reusing start-comfyui.cmd.
- How: copy restart's spawn+poll halves minus the stop; ScreenStage's PowerKeys gains the third key with the same arm-then-fire idiom.

**Restart should say flags will apply** — Value Low · Effort S
- The restart tail re-renders caliper.config.json flags onto the python command (the optimizer's applied-but-inactive flags ACTIVATE at restart); the confirm line could say so — "restart applies pending launch flags" when config flags differ from the running argv (activeServerFlags already reads them).

## Nice-to-haves

- The GET status could include the sidecar's state for a complete power picture at one endpoint. Low.
