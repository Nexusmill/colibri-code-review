# colibri bug review - src/components/ScreenStage.tsx (delta)

reviewer: ZCode (GLM-5.3, in-session) - sha256 9970abef - 2026-08-25
mode: bug (delta on dd6dc0b5, 2026-08-19) - context: screenStore contracts read in full (setLibraryOpen clears libraryMin; openJobOutputs dedupes via openedJobs ring; move/resize clamped), git 57ac85c/d85f4ac/6909725 (Library-as-window + archive era)

## Verdict

Shippable after the two fixes below. The window-OS rewrite is structurally sound; both defects are state-lifetime bugs the rewrite introduced.

## Fixed since last review

- [OLD, verified-stale] The reload-restore effect firing on bundle switch (prior review's LOW): that effect no longer exists - windows persist through the store directly. Closed by rewrite.
- [NEW MEDIUM] AgentConsole's elapsed heartbeat closed over stale `busySince` - the interval captured the pre-update state (0 on the first busy period), so after one tick the counter showed epoch seconds ("still thinking… 1778472312s") and later periods showed time-since-the-last-busy. FIX: local `t0` captured in the effect; busySince state removed (it was write-only otherwise).
- [NEW MEDIUM] Minimizing the Library unmounted it (`libraryOpen && !libraryMin`), discarding selection, filter, status, and scroll - an in-progress multi-file export selection died by peeking at a window, against the click-safe persistence rule. FIX: Library stays mounted while open, `display: none` when minimized. Harness check updated from DOM-absence to computed visibility.

## Verified-correct (adversarial passes, findings deleted)

- Taskbar LIBRARY key raising a minimized library: setLibraryOpen(true) clears libraryMin in the store - refuted.
- newestDone effect re-firing after queue removal/remount: openJobOutputs dedupes through the openedJobs ring - refuted.
- Pointer-scale division, resize clamp boundaries, z-order contract, pickFolder selection reset, SELECT ALL union-with-filter semantics, delete two-press arm timer.
