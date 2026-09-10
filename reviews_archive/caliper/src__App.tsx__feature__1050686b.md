# Colibri review — src/App.tsx (feature)

- **Source:** `src/App.tsx` · **sha256:** 1050686b
- **Reviewer:** GLM-5.3 (zai-coding-plan), in-session · **Date:** 2026-09-05 · **Mode:** feature
- **Context pack:** imports the chassis shell + all five surfaces + GameScreen + CommandPalette; the module-level ComfySocket wires ws events into queueStore; FEATURES.md `boot`, `nav-surfaces`, `command-palette`, `first-run`; prior bug review at this sha; last touch 91620a1 (2026-09-02).

## What this module does

The app root, deliberately thin: boots the bundle store + the direct-to-8188 websocket, opens the first-run wizard once (seated on Generate, suppressed when a panel is already seated — ruling 33), fits the window to a 16:9 viewport and publishes the uniform stage scale CSS variable, owns the global keyboard grammar (Ctrl+Enter queue, Ctrl+K palette, 1-5 surface switching with a typing guard), routes the five surfaces, mounts the arcade on the left screen for non-Generate surfaces, and exposes `queueFromGenerate` for the hotkey.

## Suggested add-ons

**A keyboard legend surface** — Value Low-Med · Effort S
- What: one discoverable place naming the full grammar: 1-5 surfaces, Ctrl+Enter queue, Ctrl+K palette, Escape panel close. The palette is the natural host (see uiStore review) or a footer tooltip.
- Why: the frontend protocol's five-second test — the hotkeys are real features with zero user-facing documentation; App.tsx:72-91 is the grammar's only record.
- How: static content; no behavior change.

**First-run "you have a render running" guard** — Value Low · Effort S
- What: the boot first-run offer checks panels but not a live job; a producing film run resumed by reload would land the wizard offer behind the run view's resume (the wizard resume path handles it, but the auto-offer could be suppressed while `jobs` has in-flight work, mirroring the existing panel check at App.tsx:37).
- Why: consistency of the "unless seated" guard family; marginal but cheap.

## Nice-to-haves

- `window.resizeTo` is best-effort with an honest comment; nothing to add.

## Notes

- Digits during arcade initials entry switching surfaces is DOCUMENTED INTENT (digits are the chassis hotkeys; the prior GameScreen feature review records the deliberate exclusion) — not a defect.
