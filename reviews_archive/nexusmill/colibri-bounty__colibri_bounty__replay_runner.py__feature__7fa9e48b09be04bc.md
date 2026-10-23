# colibri feature review - colibri-bounty/colibri_bounty/replay_runner.py

- source: `colibri-bounty/colibri_bounty/replay_runner.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `7fa9e48b09be04bc9436c581722ea81e67bbad75ec06963ec13ca6f75151f516`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0615 (in=3309 out=9143)

## grok-4.7 output (verbatim)

## What this module does

Offline, one-contest replay: `run_replay` extracts a contest tarball once, runs a single `scanner.scan`, scores it against judging truth, and writes the per-scanner findings dump plus truth-hash meta that S5 consumes. `safe_extract` is the traversal-rejecting extract used for that snapshot. `render_baseline_md` turns the in-memory score dicts into the regenerable P1 baseline table (precision, recall, severity accuracy, duplicate accuracy, matched/truth, scan count, elapsed).

## Suggested add-ons

### 1. Replay identity on the extract cache and the baseline
- **Value:** High
- **Effort:** S
- **What:** Stamp code-tarball sha256 next to the `.extracted` marker and refuse to reuse an extract when it mismatches; carry `truth_sha256` (already computed) and that code hash on the result dict and into the baseline table.
- **Why it helps the user:** Meta exists because judging bytes drift (knox 71→78) and unstamped baselines cannot be compared. The markdown and the return value still omit the stamp, and the extract cache keys only on `.extracted` existing, so a replaced corpus tarball is scored as if it were the contest snapshot.
- **How:** In `run_replay`, hash `code_tarball` with the same `hashlib.sha256` already used for `judging_json`. On mismatch, clear `code_dir` and call `safe_extract` again; write the hash beside `.extracted`. Add both hashes to the dict `run_replay` returns. In `render_baseline_md`, add columns (or a per-row footnote) for them. Do not merge rows that share contest+scanner but differ in `truth_sha256`.

### 2. Rescore frozen dumps when the matcher changes
- **Value:** High
- **Effort:** M
- **What:** Recompute match and metrics from `scan_findings_{scanner.name}.json` plus the judging file, gated on `scan_meta_{scanner.name}.json` `truth_sha256`, without calling the scanner.
- **Why it helps the user:** Iteration on this funnel is matcher/metrics against a fixed scan (v2-era vs v3 numbers). Re-running scanners to re-score moves time and can move the snapshot; the dump format this module already writes is the like-for-like artifact.
- **How:** New function beside `run_replay` (do not change `scanner.scan` or add an adjudicator argument). Read the dump `run_replay` writes, rebuild duck-typed objects with the four fields it serializes (`title`, `severity`, `detail`, `path`), then call `truth.load_truth`, `truth.valid_findings`, `matchm.match_findings`, `matchm.count_duplicate_claims`, and `metrics.score`. If the judging file's sha256 ≠ meta `truth_sha256`, raise and do not score. If the dump is missing fields the matcher needs, raise rather than scoring a partial object.

### 3. Per-tier replay that records a failed tier instead of a missing one
- **Value:** Med
- **Effort:** M
- **What:** One extract, N scanners, one dump+meta per `scanner.name`, returned as separate rows. A scanner exception writes an explicit failed meta and does not write a findings dump; later scanners still run. No union row.
- **Why it helps the user:** This file's job is the per-tier dumps S5 consumes, but `run_replay` is one scanner and an exception before `dump.write_text` leaves S5 unable to tell "not run" from "ran and missed." Fail-soft only helps if the failure stays visible and is not scored as zero hits.
- **How:** New `run_replay_tiers` that performs the extract-once block in `run_replay` a single time, then loops the score/dump path. Catch only `scanner.scan` failures: write `scan_meta_{scanner.name}.json` with `status: failed`, error type, and `truth_sha256`; do not write `scan_findings_*.json` and do not call `metrics.score`. Do not catch `matchm.match_findings` / `matchm.count_duplicate_claims` errors. Return one result per scanner for `render_baseline_md`; do not add a merged union row (different denominators stay separate; synthesis stays in S5).

## Nice-to-haves

- Stamp `code_basis: sherlock_head_tarball` in the meta JSON `run_replay` already writes, so the contest-start caveat in `render_baseline_md` survives on the dump S5 reads.
- If the scanner object has a `tier` attribute, copy it into `scan_meta_{scanner.name}.json` so S5 can apply the fixed tier priority without parsing `scanner.name`.
- Record match elapsed separately from scan elapsed in that meta (`t0` currently wraps only `scanner.scan`).
- Stable-sort rows in `render_baseline_md` by contest then scanner, and add a per-scanner `elapsed_s` total footer so offline cost can be ranked before any live spend.

- ACCEPT code-tarball sha256 stamp on the extract cache + baseline - VERIFIED STRONG: cache reuse keys on .extracted alone; truth_sha256 exists but the CODE snapshot is unstamped; the knox 71->78 drift class is this module's own recorded history.
- ACCEPT rescore-frozen-dumps (matcher iteration without re-scanning) - hooks exact (dump fields, meta truth_sha256 gate, matchm/metrics calls).
- ACCEPT run_replay_tiers (failed tier records status:failed meta, no dump, never scored as zero) - verified single-scanner shape today.
- DEFER 4 nice-to-haves (code_basis stamp, tier attr copy, match-vs-scan elapsed split, stable sort + elapsed footer).
