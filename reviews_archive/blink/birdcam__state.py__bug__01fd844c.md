# colibri review — birdcam/state.py

- source: `birdcam/state.py`
- reviewer: tencent/hy4-preview via hy4-review headless CLI (rung M2)
- sha256: 01fd844c97ca6bdc  (bytes at review time = commit f04d93d)
- date: 2026-09-19 16:05
- mode: bug
- context pack: prior review 9c1db7be (delta flow); consumers of
  BatchRecord.file/sha256 (upload / clean / _remove_member_files / retry
  --vanished); ClipRecord.metadata consumer enricher.clip_metadata_composite.

## Verdict
Sound. One finding raised and REFUTED on verification; a 1-line consistency
hardening applied anyway with honest labeling.

## Bugs & vulnerabilities
**[MEDIUM — REFUTED, deleted as a defect] retry_batch --rebuild leaves a stale
`enriched` verdict**
- Claim: the replacement archive inherits the old video's enrichment label.
- Verification: after rebuild=True, upload is impossible until compile_batches
  re-upserts a FRESH BatchRecord (enriched defaults to "") — upload refuses
  file-less batches and _recheck_failed only adopts rows holding a video id
  (cleared by retry). No mislabeled-upload path exists. Finding deleted per
  Phase 3.
- Hardening applied regardless: the rebuild block now also resets
  rec.enriched so the pre-compile window shows a truthful state (5-status
  cannot display a verdict for an archive that no longer exists). This is
  consistency polish, NOT a defect fix.
