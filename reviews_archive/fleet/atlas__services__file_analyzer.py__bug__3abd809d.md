# Colibri review - atlas/services/file_analyzer.py (bug, lead Phase-3 verification of the 2026-09-10 fork; DOCKET disposition)

- source: `C:\Users\User\source\repos\fleet\atlas\services\file_analyzer.py`
- model: claude-opus-5 (in-session lead; the 2026-09-10 fork report `_external_raw/atlas__services__file_analyzer.py__fork-2026-09-10.md` is INPUT)
- sha256 reviewed: `3abd809d5d767fa64a36f9a4370497d759f88f6d9a65b4176c4c7be6742b5567` (identical to the bytes the fork reviewed on 2026-09-10 - every fork line citation still holds)
- date: 2026-09-15
- mode: bug (Phase 3 lead pass; retirement test applied - fix now only if the defect costs data/money/secrets or blocks the pipeline BEFORE the code retires or is rewritten in Phase 3; otherwise docket with the call recorded)
- context pack: `find_importers`: only `atlas/services/__init__.py` (zero importers itself); nothing calls `FileAnalyzer.analyze*` outside the package (search_text); rows: FLEET-P0-SERVICES-TEMPFILE-HYGIENE (mktemp at the same four sites); fork probe re-run today: RED (25 MB fake upload buffered and written in full).

## Verdict
The fork's HIGH holds: all four analyze backends (`_analyze_audio_ffprobe` line 177, `_analyze_audio_mutagen` 272, `_analyze_video_ffprobe` 352, `_analyze_video_opencv` 433) read the untrusted file-like object to the end and write it to a `mktemp()` path with no cap. Unreachable today (no importer); Phase 3 services hardening owns it. Docketed as one row with all four sites so the fix lands once.

## Bugs & vulnerabilities (Phase 3 verdicts)

### [HIGH] unbounded read/write of untrusted file-like objects at four sites - CONFIRMED (probe RED), DOCKETED - `line 177, 272, 352, 433`
- Disposition: deferred row `FLEET-P0-FILE-ANALYZER-SIZE-BOMB` (fix shape: one bounded `_spool_to_temp(file_obj, cap)` helper used by all four; the mktemp fix from SERVICES-TEMPFILE-HYGIENE lands in the same helper).
### [LOW] `tempfile.mktemp()` TOCTOU - verified-present, already `FLEET-P0-SERVICES-TEMPFILE-HYGIENE`.
