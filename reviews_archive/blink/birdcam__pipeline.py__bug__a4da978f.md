# colibri review — birdcam/pipeline.py

- source: `birdcam/pipeline.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: a4da978f… (312 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: call sites from cli._run_pipeline (stage→compile→upload→clean) and tests (FakeBlinkClient/FakeYouTube via module refs); state machine contract from birdcam/state.py; quota economics (1600 units/upload) from README; live dry-run trace.

## Verdict

The safety machine is sound — the delete guard, hash gate, and dry-run all hold under tracing.
Biggest risk is an orphaned-duplicate-upload path: a YouTube-side failure after `videos.insert`
accepts a video releases the batch for re-upload without recording the accepted video id.

## Bugs & vulnerabilities

**[MEDIUM] Processing failure orphans an accepted upload; retry mints a duplicate** - `lines 203-231`
- What: `upload_video` succeeds (YouTube accepted the video, quota spent) → `mark_batch_uploaded`
  records the id → `wait_processing` times out or raises (transient network error, slow 2-hour
  compile processing past `processing_timeout_minutes`) → the `except` calls `_fail_batch`, which
  releases members for re-batching. Next run re-compiles and re-uploads the same content as a NEW
  video; the first one stays on the channel forever (private), unrecorded in any path->video map.
- Trigger: processing slower than the timeout (a 40-minute, ~290-clip day is realistic), or any
  `videos().list` transient failure inside `wait_processing`.
- Impact: silent channel pollution + double quota spend per occurrence; with hourly scheduling a
  flaky evening can multiply uploads.
- Fix: split the failure handling — keep `mark_batch_failed` but do NOT release members when
  `youtube_video_id` is already recorded; instead leave the batch failed with the video id and add
  a `recheck` path (poll `wait_processing` again next run) so the orphan is adopted or confirmed
  dead before a replacement upload is minted.

**[LOW] clean() deletes Blink copies with no byte verification when the archive is missing** - `line 260` (`if path.exists():`)
- What: the sha256 gate only runs when the compiled archive still exists. If the user (or a
  disk-cleanup tool) removed `staged/compilations/...`, the guard is skipped and the Blink copies
  are deleted with zero local verification — the exact opposite of the corrupt-file case, which
  blocks deletion. Inconsistent by half.
- Trigger: archive pruned/moved before `clean` runs.
- Impact: the "deletion requires verified local evidence" invariant documented in README is only
  enforced when the evidence file happens to exist.
- Fix: treat a missing archive as a SKIP with a loud message (same as mismatch), or add a config
  switch `require_archive_for_delete` (default true) making the invariant unconditional.

**[LOW] _title_for assumes the first member still exists** - `line 172` (`member = store.get(...)` → `member.created_at`)
- What: for a single-clip (individual-mode) batch whose clip record was removed from state, `member`
  is None and `member.created_at` raises AttributeError.
- Trigger: manual state editing or partial state loss between compile and upload.
- Impact: crash of the upload run (caught by the per-batch except? No — `_title_for` is called
  before the try block, so it aborts the whole upload pass).
- Fix: fall back to `batch.date` for the time component, or move the call inside the guarded region.

## Missing safeguards

- No cap on how many failed batches can accumulate before the run says so explicitly (a summary
  line listing failed batch ids would make stuck days visible in `status`-adjacent output).
- `stage` aborts the whole run on the first BlinkError from `list_clips`/`download_clip`; a
  per-clip try/except with a failure counter would let one dead clip (e.g. removed mid-download)
  strand fewer than all remaining clips.
- Duplicate-prevention second layer: a channel-side search by title template before upload would
  catch the F-1 orphans, but adds API cost — noted, not recommended at current quota.

Adversarial pass: F-1 traced end-to-end (`upload_video` → `mark_batch_uploaded` → `wait_processing`
raise → except → `_fail_batch` → `_release_members` → next-run re-batch → new video id);
CONFIRMED. The archive-missing inconsistency traced against `clean`'s only entry point; CONFIRMED.
`_title_for` edge requires external state surgery; PLAUSIBLE (unverified because it needs a
hand-mangled state file), listed as safeguard.
