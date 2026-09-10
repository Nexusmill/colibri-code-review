<!-- colibri review
source: comfy/caliper_vram.py
reviewer: glm-5.3 (ZCode session, colibri v0.2.0 protocol)
sha256: f2dbb57bbe372d7da9db08a5385df719fcb75b63b0a78ed836932ef462c971d3
date: 2026-09-06
mode: bug
context: E-1 wave (node self-identification); live-verified through :4173 + backend 8188 this session; prior reviews consulted via _manifest.json (delta reviews)
-->

## Verdict
Shippable. The self-ID addition (hashlib import, _NODE_VERSION/_SELF_SHA at import, `node` object in the /caliper/vram payload, docstring layer line) is additive; the Era-53 503/origin-guard logic is untouched and was live-verified this session (403 foreign origin, 400 bogus action, backend healthy). Deployed copy is byte-identical (sha f2dbb57b on both sides) and py_compile passes.

## Bugs & vulnerabilities
(none confirmed)

## Missing safeguards
- **[LOW] empty sha reads as drift** - `_self_sha256()` returns "" on any exception, which the client verdicts as DRIFT rather than unknown. Path is near-unreachable (the module was just imported from those bytes; an open() failure at import time on Windows would require the file deleted mid-import). Accepted: the honest degradation for a self-unreadable node is out of proportion to add a third wire state.
- Sync discipline: any future edit to this file must re-copy to custom_nodes in the same change - that is now runtime-checked (the entire point of this wave), and the footer will say so if forgotten.
