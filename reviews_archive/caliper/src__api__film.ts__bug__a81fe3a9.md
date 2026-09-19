source: src/api/film.ts
reviewer: tencent/hy4-preview (scan ladder hunt T1)
sha256: a81fe3a92dfa44d2081137843ec08899a12e1ada3a0b8ed30e3cfa6491236f99
date: 2026-09-19 12:08
mode: bug
context: film API client; BUGHUNT11 rejection patterns named in-file

Findings: 1 HIGH + 3 MEDIUM.
- [HIGH] CONFIRMED + FIXED: filmBatteryStatus's bare r.json() cast - a garbage body rejected raw into the poll loop AND a 200-with-error cast {job: undefined} = "no battery running". FIXED with the file's own named BUGHUNT11 pattern (catch-to-null + error != null + honest throw). Pinned (3 tests).
- [MEDIUM] CONFIRMED + FIXED: the empty-string error class - `data.error` truthiness let `{error: ""}` bodies resolve as success in post/filmList/autopilotList/autopilotStatus. FIXED: `data.error != null` at all four sites.
- [MEDIUM] OPEN (next session): autopilotDraftStream misreports an empty-string SSE error event as a missing plan (`streamError = ev.error ?? "the draft failed"` then truthiness check).
