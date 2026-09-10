# Spec review — vite.library.ts

- Source: E:\AI\Caliper\vite.library.ts (149 lines)
- Reviewer: ZCode fresh-context subagent
- SHA-256: 804a37c08df202f81f146213489562e96a97513755254ef496189cc02d179dc7
- Date: 2026-08-31
- Mode: spec conformance (registry: spec\library-outputs.json, server-side clauses LIB-RAIL-DISK-TRUTH, LIB-GESTURE-GRAMMAR, LIB-ZIP-EXPORT, LIB-PROVENANCE-SHARED)
- Context: library middleware (delete / export / fixture) mounted via vite.caliper.ts:503 under /api/library. Evidence: src/api/library.ts (client), src/components/ScreenStage.tsx:702 (delete call site), zipWriter.ts (read as evidence for the STORE clause).

## Verdict

PASS WITH ONE PLAUSIBLE FINDING. One low-severity boundary race on LIB-ZIP-EXPORT; all other judged clauses conform or are owned outside this file.

## Divergences

### 1. Same-minute -2/-3 guard is check-then-write: a concurrent export still overwrites — LIB-ZIP-EXPORT (PLAUSIBLE)

- **Expectation (quoted):** "same-minute exports suffix -2/-3 instead of overwriting"
- **Trigger:** Two POST /api/library/export requests with the same `dir` and `name` (or both using the same-minute default name) racing in flight — e.g. a double-press of SAVE ZIP before the first response lands, or a second browser window exporting in the same minute. vite.library.ts:118-124: `pathExists` (fs.access) is checked, then `fs.mkdir`/`fs.writeFile(abs, ...)` runs with default flag "w" (truncate). Neither the check nor the write is exclusive, so both requests resolve the same `abs`, both pass the `while (await pathExists(abs))` loop before either writes, and the second write truncates the first archive in place.
- **Behavior:** Sequential same-minute exports are correct (verified: `name.replace(/\.zip$/, `-${n++}.zip`)` starting at n=2 on the original name each iteration, so -2, -3, ... never collide with an existing file). The overwrite the clause forbids is reachable only through the concurrent window between access-check and write.
- **Why PLAUSIBLE, not CONFIRMED:** The race is CONFIRMED at code level (no exclusive open, flag "w"), but the shipped caller is a single-user local UI (ScreenStage.tsx exportZip) where a double-press must outrun the request round-trip; impact requires that timing, so user-level reachability stays plausible. Fix: open with an exclusive create — `fs.open(abs, "wx")` in a retry loop, or use flag "wx" in writeFile and bump the suffix on EEXIST.
- Confidence: PLAUSIBLE.

## UNJUDGEABLE HERE

- **LIB-RAIL-DISK-TRUTH** ("the library rail is the disk's truth") — this file exposes only /delete, /export, /fixture; no listing surface lives here. The rail's data (output subfolder scan + film folders + artifact counts) is owned by the library window UI in src/components/ (ScreenStage/library window) and whatever listing/provenance route serves it (vite.caliper.ts composition, src/stores/provenance.ts hydration). Not judgeable against this file.
- **LIB-GESTURE-GRAMMAR, UI half** — click/OPEN/DELETE grammar, the CONFIRM arming, the visible OPEN key, and the wording of the report line are owned by src/components/ScreenStage.tsx and siblings. Server side (files + record together, films naming) conforms: ScreenStage.tsx:702 sends `item.outputs` (the record's full set) with `item.promptId`, and vite.library.ts:78-88 unlinks every resolvable artifact then drops the whole record (`filter(rec => rec.promptId !== body.promptId)`) and returns `{removed, problems, films}` — what the server did. filmDependents (lines 46-60) names only films whose film.json manifest still references a deleted basename, matching "naming only films whose manifest still references the artifact".
- **LIB-ZIP-EXPORT, UI halves** — "the path is remembered" and the result line's wording ("states files + size") are client-side persistence/copy (UI store); the server returns `path`, `files` (count), `bytes` (sum) at line 125, which is the data the line needs. Selection UI (amber edge, CLEAR, SELECT ALL, rail-crossing clear) is owned by src/components/.
- **LIB-ZIP-EXPORT, byte-exactness mechanics** — owned by zipWriter.ts (read as evidence): method 0 (STORE, lines 52/67), CRC-32 IEEE table-driven, compressed size = uncompressed size = raw data length; no re-encode path exists. Conforms.
- **LIB-PROVENANCE-SHARED** — records persist server-side in provenance.json (read/write in this file; fixture prepends, delete filters); render-time record creation and browser hydration are owned by vite.caliper.ts and src/stores/provenance.ts respectively. The server-side halves visible here conform; cross-browser listing behavior after storage wipe is the client/hydration owner's to prove.
