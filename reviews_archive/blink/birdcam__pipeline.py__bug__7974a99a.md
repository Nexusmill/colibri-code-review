# colibri review — birdcam/pipeline.py (delta + security hunt)

- source: `birdcam/pipeline.py`
- reviewer: ZCode in-session (account:zai-individual-coding-plan/GLM-5.3), colibri-review v0.4.0, bug mode, security lens
- sha256: 7974a99a8e15518724734c47f8194f0f344089f7550af2e55e85c6b12be32803
- date: 2026-10-05 03:40
- context pack: prior M2+M3 reviews at eda35139 (hy4 + grok-4.3, two HIGHs); git delta
  73225de→9bc407d (enrichment fixes, songs-page description link, person-detector staging gate);
  jCodemunch outline; delete-safety invariants (sha256-vs-file, day-end holding, upload caps);
  remediation_manifest 2026-09-23 person-detector entry.

## Verdict

The safety machine is intact and the two prior HIGHs are verified fixed in current bytes. The new
person-detector staging gate fails closed exactly as the remediation entry prescribes. No new
defects found in this file; one cross-file question routed to the state.py review.

## Fixed since last review

- Enrichment result-handling inside the guarded region (prior HIGH): the unpacking and
  relative_to now sit inside the try at 269-280, failure sets batch.enriched="failed" — verified.
- Dry-run missing-archive mutation (prior HIGH): dry-run branch at 330-336 prints and continues
  without touching state — verified.

## Bugs & vulnerabilities (new findings only)

None CONFIRMED. Hunt notes:

- Person-detector gate (54-97, 121-139): fails closed on real runs (PipelineError at 75 — nothing
  staged unverified); unreadable clips are excluded with the file deleted locally and the Blink
  copy kept — matches the recorded design. The saved hit-frame goes under gitignored data/
  exclusively; nothing leaves the machine.
- clean() still refuses deletion without byte verification (494-500) and skips already-deleted
  members; upload caps and orphan-adoption (_recheck_failed never re-uploads) unchanged and sound.
- Cross-file check ROUTED (not yet a finding): `batch.songs_page` is set inside enricher at
  publish time and later read at upload time (348-350) — whether it survives a restart between the
  two depends on state.py serializing the field. Verified in the state.py review this session;
  recorded there if broken.

Adversarial pass: each hunt note above was traced through the current bytes (guard placement,
dry-run branch placement, delete ordering). Prior findings not restated.
