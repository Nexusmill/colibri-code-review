# colibri bug review - src/components/ScreenStage.tsx (delta)

source: src/components/ScreenStage.tsx · reviewer: ZCode GLM-5.3 in-session · sha256 838a818b (full sha in manifest) · 2026-09-05 · mode: bug (delta vs 9970abef @ 57ac85c 2026-08-25; cited regions read fresh in current bytes)
context: diff 92+31 region of the file (Library/one-offs/classes) + full diff review; prior review 9970abef (2 MEDIUM, both same-session fixes) carried; screenStore 33d0507d contracts.

## Verdict

Shippable - the delta is the artifact-class rename, films-own-their-assets shelf split, FirstRun mount, and double-click-to-open; both prior MEDIUM fixes verified present.

## Bugs & vulnerabilities

None new. oneOffs excludes records whose outputs are film-typed under a LIVE film row - a deleted film's records fall back to the shelf (orphan-proof); the rail scope/filter lens never edits the export set (R5 preserved: selection resolves against scope); busySince fix (t0 in effect) and Library stays-mounted-while-minimized (display:none) both verified in current bytes.

## Missing safeguards

- none new.

## Fixed since last review

- [MEDIUM] elapsed heartbeat stale closure - FIX VERIFIED (t0 captured in effect, busySince state gone).
- [MEDIUM] Library unmount-on-minimize discarding working state - FIX VERIFIED ({libraryOpen && <Library/>} + display:none).

## Verified-correct (adversarial passes)

- Film-file open path classifies text (md/txt) before audio so scripts/lyrics open as readouts; schema-lag guard's noArtifacts fallback carries the new classes; FOOTAGE mass-noun label; film count arithmetic over all classes.
