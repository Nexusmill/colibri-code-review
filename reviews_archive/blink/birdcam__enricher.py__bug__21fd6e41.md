# colibri review — birdcam/enricher.py

- source: `birdcam/enricher.py`
- reviewer: tencent/hy4-preview via hy4-review headless CLI (scan-ladder rung M2)
- sha256: 21fd6e4184e6f642  (bytes at review time = commit f04d93d)
- date: 2026-09-19 16:05
- mode: bug
- context pack: design spec docs/superpowers/specs/2026-09-19-ai-soundtrack-design.md;
  sole caller pipeline.compile_batches (guarded try/except Exception); external
  schemas verified live (OpenRouter chat, Replicate predictions+poll, minimax
  music-2.6 lyrics<=3500/prompt<=2000, seedream-5-pro size/aspect_ratio); media
  reality 1280x720 h264+aac, some clips audio-less; fakes-based test module.

## Verdict
Shippable for its role; two confirmed defects, both in the failure-handling
funnel, both fixed in the same session (see below).

## Bugs & vulnerabilities
**[MEDIUM] disk-write error escapes the per-song drop policy** - `_download`
- What: `dest.write_bytes(payload)` sat AFTER the except block, so ENOSPC/EACCES
  raised bare OSError, not EnrichError.
- Trigger: disk full or read-only staging during a song/card download.
- Impact: the song loop's `except EnrichError` missed it -> whole-batch
  enrichment aborted (paid songs discarded) instead of dropping one song.
  Posting itself stayed safe (pipeline catch-all).
- Fix: write + size check moved inside the guarded block. CONFIRMED (traced
  end to end). Test: test_disk_write_failure_raises_enrich_error.

**[LOW] naive created_at skipped UTC->local conversion** - `clip_metadata_composite`
- What: `if stamp.tzinfo is not None` skipped conversion for offset-less stamps.
- Trigger: a legacy/state-edited row with a naive ISO timestamp (current Blink
  producers always emit +00:00; no live trigger today).
- Impact: hour histogram bucketed in UTC, misleading the LLM prompt.
  PLAUSIBLE (no current producer); fixed anyway to match the inline comment.
- Fix: naive stamps get tzinfo=utc before astimezone(). Test:
  test_naive_timestamps_are_treated_as_utc.

## Fixed since scan
Both findings above are fixed on current bytes (post-fix suite: 113/113 OK).
