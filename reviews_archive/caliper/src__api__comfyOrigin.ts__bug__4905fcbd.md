source: src/api/comfyOrigin.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1, colibri bug mode, headless hy4 CLI)
sha256: 4905fcbdc8800f6a5173977d49ddd68874d50b61cb8ed84163142ed80aa1c333
date: 2026-09-19 11:30
mode: bug
context: comfyUrl portability role; BUGHUNT12 wiring law excluded up front

First-ever bug scan (never-scanned board file). 2 findings, both CONFIRMED, both remediated same session:
- [MEDIUM] resolved stored the RAW configured URL, not the origin - a path/query/userinfo rode into the ws derivation, iframe src, and footer. FIXED: resolved = u.origin.
- [MEDIUM] no generation guard - a fetch superseded by resetComfyOrigin() repopulated the origin late. FIXED: gen counter; reset bumps it.
Pins: origin normalization (path/query stripped) + superseded-fetch test in comfyOrigin.test.ts.
