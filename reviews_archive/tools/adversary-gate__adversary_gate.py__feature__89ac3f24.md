# adversary-gate/adversary_gate.py - feature review

source: C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py
reviewer: in-session GLM-5.3 (ZCode) · sha256: 89ac3f241c0e36a47931eff3e8b06449fcbaecd025ebac41b8d37611332485ce · 2026-10-08 17:46 · mode: feature
context pack: full-session deep read (tiering implementation, 10-round gate ladder); jCodemunch outline (all symbols); call sites reviewed_write.py / dispatchers / autoland fleet_config parity; prior bug-mode reviews in this manifest are context (zero feature rows existed).

## What this module does

The pre-commit adversarial review gate: sha-keyed clearances over staged blobs, the
tiered reviewer dispatch (tier-1 v4.1-flash quick rung → blind escalation to the
hy4 strong rung), the $0 local pre-gate (py_compile/ruff E9/biome/json/bash -n),
secret scrubbing of every outbound payload, scoped tree-sitter/ast windows for
oversize files, WARN-tier verdicts, sampled batch audits with a lock-safe drain,
post-commit notarization with true-rate adjudication, and the pre-push guard.

## Suggested add-ons

- **Review-cost telemetry command** — Value HIGH · Effort S
  What: `python adversary_gate.py costs [--days N]` aggregating the usage blocks
  already stamped in every `.adversary/reviews/gate_*.md` header into a table:
  model, tier, rounds, prompt/cached/completion tokens, $, and per-round latency.
  Why: the owner re-pins providers on pricing data monthly (2026-10-01,
  2026-10-08); today that data is scattered across artifact headers with no reader.
  How: `_review_header` already writes the usage dict; a read-only parser + a
  `costs` subcommand in `main()`. Hook point: `main()` subparser block.

- **Cache-hit drift alarm** — Value HIGH · Effort S
  What: when round N+1 of the same landing (same staged tree prefix) reports
  ~0 cached tokens, print a one-line warning naming the likely cause (staged
  bytes changed mid-landing → prefix rotated).
  Why: provider prompt-cache is the #1 cost lever (engineered in tranche R1 at
  ~3%→high); a silently diverging prefix is invisible today. `cached_tokens`
  already sits in the usage the artifacts record.
  How: compare consecutive artifacts' staged-sha sidecars + cached_tokens in
  `_cmd_run_snapshot` after the round completes. Hook: `_parse_completion` usage.

- **Tier-1 eligibility telemetry** — Value MED · Effort S
  What: log the eligibility decision + blocking reason (payload chars / removals /
  gated prefix / hook name / oversize) into the round sidecar.
  Why: `TIER1_MAX_CHARS` (40k) is a guess; the owner needs hit-rate data to tune
  the quick-rung share — the whole latency win depends on it.
  How: `_tier1_eligible` returns a (bool, reason) variant; `_stamp_review_meta`
  gains a field. Hook: `_cmd_run_snapshot` tier block.

- **`gate explain <path>`** — Value MED · Effort S
  What: prints why a file is unreviewed/stale — its clearance row, verdict, tier,
  artifact path, and the artifact's findings head.
  Why: today debugging "why won't this commit pass" means hand-reading
  clearance.json + matching artifacts; every agent session pays that cost.
  How: `explain` subcommand over `_load_clear` + artifact read. Hook: `main()`.

- **Degraded-tool version stamping** — Value LOW · Effort S
  What: the pre-gate's degrade lines include the tool version when present
  (ruff/biome) and the miss reason when absent.
  Why: reproducibility of "which linter was that verdict made with".
  How: `_pregate_run` already resolves the exe; capture `--version` once per run.

## Nice-to-haves

`status --json` for agent consumption; an ASCII ladder diagram in `status`
(tier1/tier2/audit flow); `audit-drain --report` summarizing audit_findings.jsonl;
a `--dry-run` for `check` that prints the tier decision without contacting models.
