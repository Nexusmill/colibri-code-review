# colibri feature review - colibri-bounty/tests/test_replay_runner.py

- source: `colibri-bounty/tests/test_replay_runner.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `9a9021acbe407f875c2274c4ecde0bb27dfdc430173d02fcd796aef831017617`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse) [effort medium - degenerate-retry regime]
- cost: ~$0.0420 (in=4076 out=5636)

## grok-4.7 output (verbatim)

## What this module does
This pytest suite locks the offline replay measurement path: tiny judging dumps and tarballs drive `replay_runner.run_replay` through `OracleScanner` and `StubScanner`, checking perfect precision/recall versus a zero floor, extraction abort, CLI exit 2 when the code tarball is missing, baseline markdown, the per-run findings dump, and the truth-sha256 sidecar. It does not touch org selection, status, or the truth helpers that decide which findings enter the denominator and how titles become match keys.

## Suggested add-ons
- **Value:** High. **Effort:** S. **What:** Pin the scored denominator to the severity/paid policy, and require `run_replay` metrics to agree with that set (the oracle case’s `matched == 2` currently hides why the informational issue dropped). **Why it helps the user:** A label-policy drift changes precision/recall with no named failure; like-for-like denominators are the number this funnel is paid to trust. **How:** Extend `test_oracle_round_trip_is_perfect` to build the expected set via `truth.valid_findings` / `truth.JudgedFinding` and assert it against `truth.PAID`, `truth.SEVERITIES`, and `truth.STOP`, then compare `metrics["truth_findings"]` and `metrics["matched"]`.

- **Value:** High. **Effort:** S. **What:** Freeze title identity (`norm_tokens` → `title_key`) for the titles this suite already scores, including case and punctuation variants, and keep `matches[].method == "exact"` only when keys are equal. **Why it helps the user:** The sidecar already catches judging-byte drift (knox class); an untested normalizer can split or merge findings without a byte change, so two replays stop being comparable. **How:** New test beside `test_oracle_round_trip_is_perfect` calling `truth.parse_judging_issues`, `truth.norm_tokens`, and `truth.title_key` on `judging_json` output, then the same titles through `rr.run_replay`.

- **Value:** Med. **Effort:** M. **What:** Offline corpus preflight: one complete contest and one judging-only contest under `BOUNTY_CORPUS_ROOT`, `cmd_status` listing the gap, `cmd_replay` exiting 0 only for the complete contest (the existing exit-2 path stays). **Why it helps the user:** Batch measurement currently discovers an unscannable contest only when replay fails; a status listing is the pre-flight and keeps the selected set explicit. **How:** `cli.cmd_status`, `cli.cmd_replay`, `cli.ORGS`, and `truth.select_contests` against a `tmp_path` tree. Filesystem only — do not extend `cli.cmd_solodit` or `cli.cmd_mirrors` into network fetches.

## Nice-to-haves
- In `test_scan_findings_dumped_for_diagnosis`, round-trip `scanner.ScanFinding` severity as well as title through `scan_findings_*.json`.
- In `test_render_baseline_md_carries_numbers`, require `matched`, `truth_findings`, and `scan_findings` in the markdown, not only the token `1.0`.
- Parametrize `judging_json` label order and assert `truth.parse_judging_issues` treats High + Sponsor Confirmed as order-insensitive.
- Let `make_tarball` take per-member bytes so a second `.sol` proves the oracle result does not depend on a one-file tree.

- ACCEPT scored-denominator policy pin (expected set built via truth.valid_findings vs PAID/SEVERITIES/STOP; metrics agree) - cited tests verified (oracle round trip, dump, baseline render).
- ACCEPT title-identity freeze (norm_tokens/title_key on the suite's own titles) - the sidecar catches byte drift but not normalizer drift.
- ACCEPT offline corpus preflight (complete vs judging-only contest; cmd_status gap listing; exit-2 path stays).
- DEFER 4 nice-to-haves (severity round-trip, baseline numeric asserts, label-order parametrize, multi-member tarball).
