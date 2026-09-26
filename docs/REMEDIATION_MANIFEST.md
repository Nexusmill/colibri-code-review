# REMEDIATION MANIFEST — colibri-code-review

> Human view of `docs/remediation_manifest.json` (the machine-readable, jCodemunch-indexed
> store, per G35). One row per fixed real defect, written in the SAME commit as the fix.
> Before "fixing" any reported finding, check here + the JSON — already-closed findings are
> recorded `verified-stale`, never re-fixed.

| Date | Commit | File | Sev | Finding | Source |
|---|---|---|---|---|---|
| 2026-09-26 | (this row's commit) | analyzer.py `load_spec` | MED | FD leak — bare `open(...).read()`, handle never closed (batch spec loads exhaust descriptors). Fixed with a `with` block; close guaranteed on the read-failure path too. | bug review 2026-09-25 @ 8afa3ca9 → perfection wave 2 |
| 2026-09-26 | (this row's commit) | analyzer.py `model_max_tokens` | LOW | HTTP response socket leak — bare `urlopen` result never closed (one per uncached model). Fixed with `with` per the app.py:21 precedent. | bug review 2026-09-25 @ 8afa3ca9 → perfection wave 2 |
| 2026-09-26 | (this row's commit) | analyzer.py `review_code` | MED | `max_tokens` AUTO comment/code divergence — comment said `None/<=0`, code only mapped `None`/`0`; negatives (reachable via `run_batch --max-tokens`) hit a 400 instead of the ceiling. Predicate now `(_mt or 0) > 0`. | perfection L2 pass A 2026-09-26 (new) → wave 2 |
| 2026-09-26 | (this row's commit) | analyzer.py mode gate | MED | Unknown `mode` silently coerced to "bug" — a caller typo got a billed bug review with no signal. Now a loud ValueError naming the bad value and the full valid set, raised before any client construction. | quality review 2026-09-26 (tranche 3) → perfection wave 3 |
| 2026-09-26 | (this row's commit) | analyzer.py `_call_retry` | MED | One transient API error (429/5xx/conn) errored the whole file; re-run re-paid input tokens for the set. Bounded transient retry (base·2^(a-1) backoff, cfg-tunable, 3-attempt default) now wraps both the primary and corrective calls; non-transient 4xx raises at once. Amended EV-136 (commit-gate catch): total `_transient` predicate, attempts≥1/base≥0/60s-cap guards, direct unit tests — net 109/109. | quality review 2026-09-26 (tranche 4) → perfection wave 4 |

Verification pattern for all rows: RED-first tests in `tests/test_analyzer.py` (failed on
pre-fix bytes), mutation checks reverting each fix re-turn them RED, full battery green.
