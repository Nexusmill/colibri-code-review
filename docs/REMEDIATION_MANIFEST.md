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
| 2026-09-26 | (this row's commit) | analyzer.py client / ceiling cache / spec filter | MED | Stage-E blind review (hy4) found 3 CONFIRMED defects the local passes missed: per-call OpenAI client never closed; ceiling cache keyed by model only (wrong ceiling on live api_base switches); numeric registry ids never matched the string filter (spec mode died on numeric-id registries). Fixed: `with OpenAI(...) as client`, tuple cache key (failure-caching of the high-safe fallback kept by adjudication), `str()`-normalized rid. Net 122/122, mutations RED-OK. | perfection Stage E blind → wave 7 |
| 2026-09-26 | (this row's commit) | analyzer.py clause render / plan-prior block / retry finish | MED | Stage-E COLD pass (grok-4.6, blind) found 3 more CONFIRMED defects: `if v:` dropped False/0 spec clauses (the quiet clauses spec mode judges); plan mode + prior got delta wording contradicting the plan contract; corrective-retry success left `usage["finish"]` stale. Fixed with the pinned empty-string skip preserved, a mode-aware prior block, and finish updated on retry success. Amended EV-137 (commit-gate catch): `first_finish` preserves the primary attempt's signal. Net 129/129, mutations RED-OK. | perfection Stage E cold pass → wave 8 |
| 2026-09-26 | (this row's commit) | analyzer.py client ctor / registry guards | MED | COLD pass 2: the SDK's default `max_retries=2` stacked with `_call_retry` (up to 9 HTTP requests for an advertised budget of 3 — client now built with `max_retries=0`, the cfg knob is the total HTTP budget); malformed registries crashed `load_spec` with AttributeError (non-list `controls` passes through raw; non-dict rows skipped). C5 failure-caching dispute upheld per the wave-7 adjudication. Net 132/132. | perfection Stage E cold pass 2 → wave 9 |
| 2026-09-26 | (this row's commit) | analyzer.py load_spec row fields | LOW | Cold pass 3 (qwen3.8-flash, 3rd family; all its MED+ adjudicated for the single-user-local trust model — table gate-cleared in junk/): the wave-8 truthiness cure missed the row-header fields — `label` 0/False fell to feature, `status` 0/False dropped, empty `contract` swallowed `expected`. Presence-checks now match the wave-8 predicate style. Net 135/135, M-W10a/b RED-OK. | perfection Stage E cold pass 3 → wave 10 |

Verification pattern for the preceding historical rows: RED-first tests in `tests/test_analyzer.py` (failed on
pre-fix bytes), mutation checks reverting each fix re-turn them RED, full battery green.


## 2026-09-27: fresh review remediation R01-R17

Verified actual applied files on 2026-09-27: tests/test_analyzer.py 135/135; tests/test_sweep_fixes.py 2/2; tests/test_scanner_ext.py 11/11; pytest tests/test_agent_error_rates.py tests/test_review_remediation.py tests/test_console_remediation.py 75 passed. All commands exit 0. Offline tests; browser/live-provider behavior not exercised.

Primary reviewer: Codex in-session. Required independent pre-write reviews used Qwen 3.8 Flash and the user-selected openai/gpt-6-luna-pro. Every applied source/test change received CLEAR for its exact bytes; commit clearance is a separate required step. Existing unrelated staged evidence-docket changes are excluded from this repair.

| ID | Severity | File | Verified repair |
|---|---|---|---|
| R01 | HIGH | `run_batch.py` | Account for billed usage before either save; stop future dispatch after paid persistence failure; retain response and usage in summary or terminal recovery JSON when summary storage also fails. Added terminal recovery JSON if both report and summary persistence fail, and save requested output before cache completion so retry remains possible. |
| R02 | MEDIUM | `app.py` | Require explicit complete response status from analyzer; incomplete/refused/truncated/invalid responses retain evidence and cost but no completed-cache credit. Failed retries preserve prior completed reviews, immutable bodies and total attempt cost. Exports and console label completed modes separately. Contradictory finish fields, empty or nonstring replies cannot earn new credit. Legacy canonical records without completion flags retain historical status for compatibility. |
| R03 | MEDIUM | `app.py` | store.read_source reads one byte buffer for both SHA-256 and decoded review text; app and batch use that paired result. |
| R04 | MEDIUM | `store.py` | modes_done counts only current completed bug, quality and feature records. |
| R05 | MEDIUM | `run_batch.py` | Resolve batch cache from enclosing repository or requested directory, with validated --root override, independent of matching file distribution. Linked-directory aliases use consistent lexical path spelling; actual Windows junction regression. |
| R06 | MEDIUM | `analyzer.py` | Validate required review JSON fields, finding types/severity/line and notes before accepting either primary or corrective response. |
| R07 | MEDIUM | `tests/test_sweep_fixes.py` | Budget regression requires successful exit, zero errors, nonzero completed calls, independent billed ledger and bounded dispatch; paid storage failures have dedicated regressions. |
| R08 | MEDIUM | `store.py` | Include normalized full source-path digest and unique attempt ID in report filenames; atomically save via unique temporary files and retain attempt history. Readable filename tail shortened to preserve representative Windows path budget. |
| R09 | MEDIUM | `app.py` | Read endpoint controls before AUTO lookup and pass selected model plus endpoint to the same ceiling lookup used by execution. |
| R10 | MEDIUM | `app.py` | Repeat source input and output per queued mode; meter accepts explicitly pre-summed input. Confirmation builds full prompts including system/spec/prior/static context; all amounts are labeled estimates, not spending caps. |
| R11 | MEDIUM | `run_batch.py` | Reuse scanner discovery in directory batch walks, including secret/vendor/scratch/venv/size exclusions; normalize glob strings and validate pattern elements. Local scanner import follows path setup, verified in safe-path subprocess mode. |
| R12 | MEDIUM | `store.py` | Persist root-relative output references and resolve them against the selected store root, including moved legacy paths; preserve canonical source identities during relocation conflicts. Ambiguous foreign-to-foreign mappings remain distinct; nested legacy review-directory references use the nearest review-directory component. Malformed rows do not erase good rows; deeply nested invalid JSON is recoverable. |
| R13 | LOW | `store.py` | Normalize source keys with absolute paths and Windows case folding; combine legacy case-variant mode records. |
| R14 | LOW | `scanner.py` | Match actual vendor directory components and generated-file suffixes; retain authored mapper and helper names, including POSIX literal-backslash filenames. |
| R15 | LOW | `static_context.py` | Treat .mjs, .cjs, .mts and .cts as explicitly non-Python even when text happens to parse as Python. |
| R16 | MEDIUM | `agent_error_rates.py` | Record missing parent review-directory anomaly and continue collecting linked-worktree denial evidence. |
| R17 | LOW | `agent_error_rates.py` | Sort same-second denial artifacts by numeric collision sequence with unsuffixed first; report ambiguous cross-worktree ties. |

Completion compatibility: new save calls require consistent completion evidence and nonempty text; existing canonical manifest rows without a completion flag retain their historical status. Tests exercise actual Windows case folding and a real junction; POSIX literal-backslash behavior is checked with POSIX path semantics on Windows.

R02 migration boundary: the new-write defect is fixed. Previously saved records without completion metadata are not revalidated and may include historical incomplete results; use a forced fresh review to replace an uncertain record. No retrospective certification of those records is claimed.

Commit-gate R10 follow-up: queue estimates now reuse expensive static enrichment within a session. Current source/path/mode/settings/prior/specification and prompt/builder version control invalidation; cache retains only current queue. The regression failed with two unchanged prompt builds before the fix and passes after it. Full focused suite now 75 passed on actual applied files. First-time estimation can still run the selected tools, as documented in CONSOLE.md.
