# bug review — KokoroBookReader/reader/cast_ui.py
- source: KokoroBookReader/reader/cast_ui.py
- reviewer: in-session GLM-5.3 (ZCode), colibri-review v0.4.0 debug+bug pass
- sha256: 7a5e06732779e290786dba17f32b246ba6e79b4d54c4e0e0c180d24c9186b35b
- date: 2026-09-22
- mode: bug (post-fix verification pass; debug ladder run this session)
- context pack: load_cached_cast/_show_detected_cast/_save_detected_cast/_analysis_progress sources; narration.json state for the owner's book (saved legacy analysis present, no refined result.json); tests test_cast_flow (make_window harness).

## Verdict
Shippable after this session's fix.

## Bugs & vulnerabilities (found this session, fixed in this commit)
**[HIGH] Improved-scan progress status was unreachable for books with a saved legacy cast** - load_cached_cast (pre-fix line ~85)
- What: `saved = narration_store.analysis(book); if saved: show; return` ran before the refined-marker branch, so for the owner's book (completed v2 scan saved) the reopen line was only "Earlier scan: use Scan / improve characters to recheck speaker assignments." — no word of the 130/360 saved sections.
- Impact: combined with the counter restarting at 1/360, the owner read a resume as a total loss.
- Fix: the refined resume note is computed first and appended to the saved-cast line; the no-saved branch shows it as the primary line. Verified live offscreen with the owner's real library/store.
**[MEDIUM] Reopen status trusted the marker's saved field** - load_cached_cast
- What: displayed marker["saved"] (last run's position: 3) instead of the on-disk cache (130).
- Fix: counts batch files on disk (excluding index/result/progress), capped at the marker total; version-mismatch branch preserved; result.json-present fall-through to the legacy probe preserved.
