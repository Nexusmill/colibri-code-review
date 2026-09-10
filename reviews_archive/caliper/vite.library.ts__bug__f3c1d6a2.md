# colibri bug review - vite.library.ts (delta)

source: vite.library.ts · reviewer: ZCode GLM-5.3 in-session · sha256 f3c1d6a2 (full sha in manifest) · 2026-09-05 · mode: bug (delta vs f9aaff24 @ 5cfba4b 2026-08-22)
context: diff 38+11; prior review f9aaff24 (clean) carried; FIXTURE_WAV header bytes hand-verified (RIFF sizes, PCM mono 8-bit 8kHz, blockAlign/byteRate, 0x80 silence fill).

## Verdict

Shippable - the delta fixes the export race and re-homes the fixture honestly.

## Bugs & vulnerabilities

None new. Exclusive-create (wx) with suffix bump closes the check-then-write export collision window (two concurrent exports can no longer overwrite); the fixture now seeds an output-dir ONE-OFF (type "output", Caliper/fixtures subfolder) so the film/one-off provenance split keeps it on the shelf; FIXTURE_WAV is a well-formed 1s silent WAV.

## Missing safeguards

- none new (prior review's traversal/collision findings remain fixed).

## Fixed since last review

- (prior was clean; the export race fix lands in this delta)

## Verified-correct

- wx-retry loop rethrows non-EEXIST; boundary check unchanged (root + path.sep containment before any write).
