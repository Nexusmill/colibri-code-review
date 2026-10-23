# colibri feature review - colibri-bounty/colibri_bounty/cli.py

- source: `colibri-bounty/colibri_bounty/cli.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `e14c895c566420cf0b06a01355a29f10443e0c1932779e8a6e22c663b22f3b45`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0554 (in=4069 out=7884)

## grok-4.7 output (verbatim)

## What this module does

This is the shell entry point for colibri-bounty: argparse subcommands that sync the corpus (Solodit, the `ORGS` GitHub orgs, mirrors), print or write corpus status, and run an offline Sherlock replay. `cmd_replay` selects a hardcoded 10-contest set (or one `--contest`), runs oracle/stub/p2/p2x via `replay_runner.run_replay`, prints per-contest precision/recall plus LLM spend, and can overwrite `docs/REPLAY_BASELINE.md`. It does not implement scanning or matching; harnesses drive the library only through these commands.

## Suggested add-ons

### Pooled count line for this invocation's own denominator
Value: High
Effort: S
What: After the contest loop, print one pooled fraction — sum of `metrics.matched` over sum of `metrics.truth_findings`, plus contest count and `--run` — labeled as pooled counts, not the mean of the per-contest precisions, and put that same fraction in the written baseline.
Why: Published funnel numbers are pooled counts (16/60, 13/48). This command only prints per-contest P/R, so a harness that averages those percentages will not match the run's real denominator, and nothing in stdout or `REPLAY_BASELINE.md` states the total.
How: In `cmd_replay`, reduce the `results` list already appended in the `for name, _ in pair` loop, before the `args.write` block. Prepend that line to the string passed to `out.write_text` alongside `replay_runner.render_baseline_md`. Keep it scoped to this invocation's `results` only; do not fold in any other tier's table.

### Run-level spend cap with an explicit truncated set
Value: High
Effort: S
What: `--max-cost` on `replay`. Sum `last_stats["llm_usage"]["cost_usd"]` as contests finish; do not start another contest once the next one would exceed the cap; print completed vs selected and the names not run; mark that truncation in anything `--write` emits; return non-zero when the cap stops the loop.
Why: Paid spend is supposed to be capped and disclosed. The only cap visible here is per scanner instance (`budget_stopped` is printed, then the loop continues and `cmd_replay` returns 0). A 10-contest p2/p2x run is ten budgets, and a harness cannot tell a full measurement from a spend-truncated one.
How: In `main`, on the replay parser, `r.add_argument("--max-cost", type=float, default=None)`. In `cmd_replay`, after the existing `last_stats` / `llm_usage` print, add `cost_usd` to a running total and `break` before the next `replay_runner.run_replay` when the cap is hit. List the skipped names from `pair`. On the write path, record truncated plus skipped names next to `replay_runner.render_baseline_md`. Leave each scanner's own `budget_stopped` behavior unchanged. Do not drop contest lines already printed.

### Pin the contest set and the baseline path from the CLI
Value: High
Effort: S
What: `--want` (default 10) forwarded into selection, repeatable `--contest`, and `--out` so a run need not clobber `docs/REPLAY_BASELINE.md`. Write the resolved contest names and `--run` into the artifact.
Why: `want=10` and a single optional contest are hardcoded in `cmd_replay`, and `--write` always targets one path. Reproducing a published subset, or keeping the previous baseline so two denominators are not overwritten into one file, currently means editing this module. This does not change how contests are chosen — only exposes the selector and the output path.
How: In `main`, on the replay parser: `r.add_argument("--want", type=int, default=10)`, change `--contest` to `action="append"`, add `--out` (default None). In `cmd_replay`, pass `want=args.want` to `truth.select_contests`. If `args.contest` is a list, build `pair` with the judging-json and tarball checks the single-contest branch already uses (`issues_dir / f"{name}-judging.json"`, `sherlock_dir / f"{name}.tar.gz"`). Write block: use `args.out` when set, otherwise the current `cfg.PROJECT_DIR / "docs" / "REPLAY_BASELINE.md"` path; include the resolved names and `args.run` in the `write_text` payload next to `replay_runner.render_baseline_md`.

## Nice-to-haves

- `--json` on `cmd_replay` and `cmd_status` dumping the `results` list and the `status.corpus_status` object already in hand, so harnesses stop scraping print lines.
- `cmd_status`: pass a UTC timestamp into `status.render_md` instead of `generated_at="now"`, the same clock `cmd_replay` already uses for `replay_runner.render_baseline_md`.
- `--list-contests`: also print whether the judging dump and tarball exist, using the same path checks `cmd_replay` runs before `replay_runner.run_replay`.
- Optional `--write` on `cmd_solodit`, `_sync_org_cmd`, and `cmd_mirrors` to drop the `rep` / `stats` / `results` object beside the status doc, so sync failures are artifacts as well as exit codes.

- ACCEPT pooled-count line for the invocation's own denominator - VERIFIED: cmd_replay prints per-contest P/R only; published figures (16/60, 13/48) are pooled counts an averager cannot reproduce.
- ACCEPT --max-cost run-level spend cap with explicit truncated set + non-zero exit - VERIFIED: per-scanner budget_stopped prints but the contest loop continues and returns 0; ten budgets are invisible at run level.
- ACCEPT --want / repeatable --contest / --out (selector + baseline path exposed, selection logic unchanged) - all three hardcoded today.
- DEFER 4 nice-to-haves (--json dump, UTC clock for cmd_status [it literally passes generated_at="now"], --list-contests artifact checks, sync --write).
