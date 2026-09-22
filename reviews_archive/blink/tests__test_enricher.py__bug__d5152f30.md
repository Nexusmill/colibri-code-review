# colibri review — tests/test_enricher.py

- source: `tests/test_enricher.py`
- reviewer: tencent/hy4-preview via hy4-review headless CLI (rung M2)
- sha256: d5152f300e68add8  (bytes at review time = commit f04d93d)
- date: 2026-09-19 16:05
- mode: bug
- context pack: contract source birdcam/enricher.py (enrich_compilation
  orchestration, ffmpeg arg builders, _guard_url, run_replicate polling,
  composite builder); test-specific hunt classes per protocol.

## Verdict
Two real test defects (one tautology, one missing contract pin); both fixed.

## Bugs & vulnerabilities
**[MEDIUM — CONFIRMED] tautological assertion** — test_single_song_skips_concat_filter
- `assertNotIn("filter_complex", args)` checks list membership of a string
  without the leading hyphen; an arg of "-filter_complex" would never match,
  so the assertion cannot fail.
- Fix: assertNotIn("-filter_complex", args) plus a positive control on the
  two-song case. Fixed.

**[MEDIUM — CONFIRMED] card-failure path did not pin the workdir-cleanup
contract** — test_card_failure_falls_back_to_plain
- The LLM-failure test asserted workdir removal; the card-failure test did
  not, leaving a leak regression undetectable.
- Fix: workdir absence now asserted on that path too. Fixed.
