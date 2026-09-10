# colibri bug review - src/stores/screenStore.ts (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 dc83b754 - 2026-08-26
mode: bug (delta on 12c274e7, 2026-08-19) - context: the Era-24 window-system rewrite (6909725/d85f4ac/57ac85c) re-read in full alongside ScreenStage's consumers; persisted-state surface (windows, openedJobs, library geometry)

## Verdict

Shippable - the delta is clean.

## New findings

None confirmed. The prior bounds invariant holds through the rewrite (move clamps by footprint; resize caps at remaining space; maximize fills exactly above the taskbar and restores exact bounds). openAsset's key-dedupe/raise, openJobOutputs' openedJobs ring (49-cap) with close-marks-seen, setLibraryOpen's unminimize+raise, and assetFromOutputs' audio-less null (consistent with MediaView's known no-solo-audio design) all traced.

## Missing safeguards

- Persisted windows restore whatever geometry was saved; a future SCREEN_W/H change would clamp only on interaction, not at rehydrate (no current mismatch).
