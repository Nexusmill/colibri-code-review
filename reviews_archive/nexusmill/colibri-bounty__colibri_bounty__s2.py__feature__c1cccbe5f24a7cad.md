# colibri feature review - colibri-bounty/colibri_bounty/s2.py

- source: `colibri-bounty/colibri_bounty/s2.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `c1cccbe5f24a7cad162026d76942a706533718ff7a3f98e4f6a537b0f67cf487`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0259 (in=2343 out=3528)

## grok-4.7 output (verbatim)

## What this module does

`dump_findings` is the S2 write boundary: it persists an already-adjudicated candidate list to `scan_findings_s2_inv.json` under the replay directory and returns that path. The on-disk shape is a bare JSON list of `{title, severity, detail, path}`, and the docstring requires `detail` to cite the failing invariant plus observed values. Raw invariant failures never enter this file; only post-adjudication candidates do.

## Suggested add-ons

**Value: High. Effort: S.** Adjudication ledger beside the candidate list. What: extend `dump_findings` with optional keyword args (`raw_failures`, `trace_refs`) and write a sidecar (same stem, `.meta.json`) recording `n_raw`, `n_adjudicated`, and trace paths — never the raw failures themselves as findings. Why: the napier case (4 raw, 0 real) is invisible in a bare list, so a later union cannot tell "tier ran, adjudication rejected everything" from "tier never ran," which breaks like-for-like denominators. How: keep the existing list file untouched for `tests/test_s2.py`; add the counts only in the sidecar written by `dump_findings`.

**Value: High. Effort: S.** Execution-grounded shape gate at the write. What: before `json.dumps`, require each item to have `title`, `severity`, `detail`, `path`, and a `detail` that names an invariant and an observed value; raise on violation so a bad dump is not a silent empty-or-partial tier result. Why: this function is the only place that contract exists, and S5 will treat whatever lands in `scan_findings_s2_inv.json` as inv-tier findings. How: private helper called from `dump_findings` (stdlib only); do not filter-and-continue.

**Value: Med. Effort: S.** Canonical byte-stable dump. What: sort candidates by `(path, title)` and dump with stable separators so two replays of the same adjudicated set compare equal. Why: corpus replay is the product; unordered lists make precision/recall diffs noisy without changing the measurement. How: sort inside `dump_findings` immediately before `write_text`.

## Nice-to-haves

- Module-level filename constant for `scan_findings_s2_inv.json`, shared by `dump_findings` and tests, so S5 does not hardcode the stem.
- `load_findings(replay_dir)` twin that reads that constant and returns the list, so consumers do not reimplement the path.
- `schema_version` on the sidecar only, so the candidate list format can stay a bare array while the ledger evolves.

- ACCEPT adjudication ledger sidecar (n_raw/n_adjudicated/trace refs) - VERIFIED: dump is a bare list; the module's own napier arc (4 raw, 0 real) is indistinguishable from "tier never ran" downstream.
- ACCEPT execution-grounded shape gate at the write boundary - the detail-must-cite-invariant contract is docstring-only today.
- ACCEPT canonical byte-stable dump (sort by path,title + stable separators).
- DEFER 3 nice-to-haves (filename constant shared with s5, load_findings twin, sidecar schema_version).
