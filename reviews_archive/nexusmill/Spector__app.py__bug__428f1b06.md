# Colibri Review - bug (FULL re-audit) - Spector/app.py

- **Source path:** `Spector/app.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 50
- **sha256 reviewed:** `428f1b06b92bf22afe4812708860179fa837c9940388be4f9835b50c6d8094b0` (sha8 `428f1b06`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: this file's prior audits predate the adversarial gate and cannot be trusted - no delta against them)
- **Context pack:** FULL read of the current bytes (owner ruling 2026-09-10: the file's reviews of 2026-07-19..08-15 predate the gate and are untrusted); jCodemunch `get_file_outline` + `find_importers`; the prior review records and the remediation/deferred rows for the file loaded as CLAIMS to re-verify, not as baseline; call sites traced with `get_symbol_source`.

## Verdict
Clean at this read (1569 lines). The origin/host/token guard, the version bump under one lock, the SSE condition sharing that lock, the bounded heavy routes, the async job queue's finalize sweep and the temp-file `call_on_close` cleanup all trace end to end; every user-controlled number is parsed with a clean 400; the CSV export neutralises formula cells; the pack import and export routes hand the warehouse the temp path and always remove it.

## Bugs & vulnerabilities
None confirmed.

## Adversarial verification pass / notes
- Candidates traced and dropped: `/api/reproduce` download name from the URL (werkzeug quotes/encodes `Content-Disposition`); `_dupe_hit` re-parsing the upload before ingest (double work, not a defect); `/api/duplicates/resolve` on a cluster containing a dedup parent (the per-item delete refuses and reports).
