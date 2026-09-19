source: src/components/FilmRuns.tsx
reviewer: tencent/hy4-preview (scan ladder hunt T1)
sha256: 6c58151a6748f37a01fe260f8f6f0ae1b998ee8758eaf25f983b35c6b55f34b6
date: 2026-09-19 11:35
mode: bug
context: LIST-FIRST window; TESTFILEHUNT-era test remediation excluded; armed-verb doctrine relevant

First-ever bug scan. 2 findings:
- [MEDIUM] CONFIRMED + FIXED: confirmDelete's catch set the error alert but left the armed "to the Recycle Bin" intention in the footer beside it - the footer kept promising a bin trip the server refused. FIXED: the catch clears the intention; the alert speaks the failure. Pinned.
- [LOW] REFUTED: the DELETE arm's status line called an intention, not a server report. Refuted by precedent - armed-verb copy naming what the second press does is the app's established pattern (SettingsConsole presets, bundles remove); the CONFIRM button is the press's visible result.
