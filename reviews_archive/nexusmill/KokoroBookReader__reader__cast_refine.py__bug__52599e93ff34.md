# bug review — KokoroBookReader/reader/cast_refine.py
- source: KokoroBookReader/reader/cast_refine.py
- reviewer: in-session GLM-5.3 (ZCode), colibri-review v0.4.0 debug+bug pass
- sha256: 52599e93ff34d10b551f7dbfb00ab261e3f718427e5c3df9accf1bea137ee472
- date: 2026-09-22
- mode: bug (post-fix verification pass; debug ladder run this session)
- context pack: analyze_refined/ask_refined/checked_answers/atomic_json sources; cast_scan.CastScanJob.run probe-then-real protocol; on-disk cache forensics (130 batch files, 41 containing retryable poison, mtimes 04:50-08:21); tripwire re-run on the owner's real book; tests test_cast_refine/test_refine_retry_cache/test_cast_flow.

## Verdict
Shippable after this session's fix. The file's resume machinery was sound (keys deterministic across processes and hash seeds — verified live), but one design rule turned deterministic model denials into eternal re-asks.

## Bugs & vulnerabilities (found this session, fixed in this commit)
**[HIGH] Saved sections containing retryable answers were re-asked on every scan** - analyze_refined cache-read block (pre-fix line ~176)
- What: `if any(a.get("retryable") is True ...): answers=None` discarded a structurally valid cached batch whenever one quotation had failed model validation, so the whole batch was re-asked.
- Trigger: ask_refined surrenders per-utterance with retryable=True after bounded splits/repairs; the analyzer is deterministic (temperature 0, same payload), so the same quotations fail every run (live example: u20 "Myne, I'll explain to Lutz..." whose speaker "Mom" is rejected by speaker_name every time — cached 08:21 with the identical denial).
- Impact: 41 of the owner's 130 saved batches re-asked per scan (~1 in 3): hours of repeated GPU work, the progress counter re-walking "saved" ground, and the owner-visible "all progress lost".
- Fix: a saved section is terminal; cached answers are reused as-is and unresolved quotations stay flagged for manual review. CONFIRMED by disk forensics + tripwire verification (130/130 reused, zero model calls, first genuine miss at the true frontier u796).
**[MEDIUM] progress.json recorded the last run's loop position, not the cache truth** - analyze_refined marker write (pre-fix line ~186)
- What: saved=number+1 only; an early close left 3 on disk while 130 sections were cached.
- Fix: initial marker written from the on-disk batch count; per-batch value max(disk_count, position); marker writes are best-effort (mark_progress) so a transiently locked marker cannot abort the scan (also hardens the pre-existing atomic_json final-replace raise path).
**[LOW] Progress messages did not distinguish reused from newly analyzed sections** - analyze_refined loop
- Fix: "saved section reused." vs "new section analyzed and saved." plus the pre-loop resume banner "N of M sections already saved".

## Fixed since last review
- The round-50 queued items (v2 chunk boundaries, v2 name normalization, tryLock discrimination) remain open and untouched by this pass.
