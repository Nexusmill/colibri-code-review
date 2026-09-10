# colibri review — birdcam/state.py

- source: `birdcam/state.py`
- reviewer: in-session (zai-coding-plan/GLM-5.3-Flash), colibri-review v0.2.0 bug mode
- sha256: 9c1db7be… (228 lines, bytes on disk at review time)
- date: 2026-09-05
- context pack: consumers pipeline.py (all mutators), tests (transition + guard cases); invariant: deletion only from confirmed, confirmed only via a batch whose YouTube processing succeeded; save() is tmp+os.replace atomic.

## Verdict

The guard machine is correct and well-tested; the one real weakness is that a corrupted state
file bricks every command with a JSON traceback and no recovery path.

## Bugs & vulnerabilities

**[LOW] Corrupt state.json crashes every command with no recovery path** - `line 93` (`raw = json.load(fh)`)
- What: `_load` lets `json.JSONDecodeError` propagate; stage/upload/clean/status all die at
  startup. Because `save()` writes atomically there is no torn-file risk from the pipeline itself,
  but a user edit, disk issue, or partial manual merge produces an unrecoverable-looking wall.
- Trigger: hand-edited or externally damaged `data/state.json`.
- Impact: total pipeline outage with an unfriendly message; the fix is out of band because the
  file is the only copy of the safety evidence.
- Fix: catch the decode error, raise `StateError("state.json is corrupt; move it aside and re-run
  (staged clips will be re-listed; already-deleted Blink clips would be re-staged — check
  backups)")`, and rotate the bad file to `state.json.bad-<ts>`.

## Missing safeguards

- No state schema version field — future field changes can't detect/migrate old files (cheap to
  add now: `"version": 1` next to `clips`).
- `mark_clip_confirmed` allows a clip whose batch record was deleted in a prior partial run to be
  confirmed (clip.batch_id set, batch gone) — unreachable through the pipeline (batch deleted only
  after all members), noted for manual-edit reality.
- Sorting by the ISO `created_at` string assumes uniform offsets; true today (Blink emits +00:00
  everywhere) — would mis-sort if that ever changed.

Adversarial pass: decode-crash traced through every subcommand entry (`_store(config)` in cli);
CONFIRMED. Batch-deleted/member-confirmed reachability walked the pipeline call order — not
reachable through the code, refuted as a bug, retained as a safeguard note.
