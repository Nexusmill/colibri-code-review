# colibri bug review - vite.config.ts (delta)

source: vite.config.ts · reviewer: ZCode GLM-5.3 in-session · sha256 f8ce84f6 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs a29d8658 @ e8dd8ef 2026-08-19)
context: diff 8+6; prior review a29d8658 carried; the 403-Origin lesson (ComfyUI 0.33 aiohttp) in mind.

## Verdict

Shippable - typing + portability only.

## Bugs & vulnerabilities

None new. stripOrigin/stripOriginWs now typed as HttpProxy.Server (the structural type had drifted); comfy target follows COMFY_URL.

## Missing safeguards

- (unchanged, documented) the websocket connects DIRECT to 8188 by design; only HTTP paths ride the proxy.

## Fixed since last review

- (prior had no open findings)
