# colibri feature review - colibri-bounty/colibri_bounty/p2_static.py

- source: `colibri-bounty/colibri_bounty/p2_static.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `c55b649a6408e0ba96dfbdd75206291569bb314218c87ea48e618a16bb68e25c`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: module role + consumers + deliberate-decisions list (MATCHER_V3.md, gate EV-241/EV-245 lineage) + already-planned exclusions (FUNNEL_PLAN S1/S2v2/W6) + RSI ruleset (0 active) + remediation manifest (p2_llm slug pin)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0529 (in=5772 out=6888)

## grok-4.7 output (verbatim)

## What this module does

This is the S1 static tier: it discovers non-dependency `.sol` files, resolves a pragma (or nearest installed) solc, prepares known Foundry pins, and fail-soft fan-out runs Slither per file with a per-file forge-vs-solc choice. Stdout JSON is parsed into `StaticHit` records plus coverage stats for the LLM funnel in `p2_scanner.py`. Compile failures, runner crashes, and dep-prep errors skip or count and never abort the scan.

## Suggested add-ons

**1. Opt-in hit budget for the LLM consumer**
- Value: High
- Effort: S
- What: Rank `StaticHit`s by impact then confidence and cap how many leave the tier, without changing the default unfiltered return.
- Why it helps the user: Paid spend is capped, and Slither’s informational/optimization checks dilute the prompt the funnel actually pays for. A budget keeps high-impact checks in context while full counts stay measurable.
- How: Add `select_hits(hits, *, max_hits, min_impact)` next to `parse_slither_json`, ordering on `StaticHit.impact` / `StaticHit.confidence`. Call it at the end of `scan_static` only when the caller passes a budget (default `None` = today’s list). Record `hits_total` vs `hits_emitted` on the existing `stats` dict so coverage stays honest.

**2. Foundry-pinned solc when the file is on the forge path**
- Value: High
- Effort: S
- What: If `framework_for` is foundry, prefer `solc` / `solc_version` from that project’s `foundry.toml` over the pragma sniff, then fall back to `_resolve_solc`.
- Why it helps the user: Contest repos pin the compiler that actually builds them. `_resolve_solc` only sees the first semver in the first 800 characters, so a caret or late pragma selects the wrong artifact and the file is skipped — lost hits, understated `files_analyzed`.
- How: Add `_foundry_solc(root)` beside `_remapping_pins`, reading the toml at `_foundry_root` with the same line-oriented style. In the `scan_static` loop, use it only when `use_solc` is not injected and `framework_for(path, code_dir)` is foundry; pass the result through `solc_binary` as today. Missing or unknown pins still fail-soft via the existing skip path.

**3. Bounded parallel fan-out**
- Value: High
- Effort: M
- What: Run the per-file Slither subprocesses concurrently, with a small worker cap, after dep prep.
- Why it helps the user: Replay is sequential today, and each file can sit on `default_runner`’s 180s timeout. Corpus passes are dominated by wait time, not by parsing.
- How: Keep the `foundry_prepare` / `_foundry_root` loop single-threaded (forge installs must not race). Parallelize only the `for path in files` body in `scan_static` (a thread pool around `runner`, which is already a blocking `subprocess.run`). Each worker returns `(hits, stat_delta)` and the main thread merges into `stats` so one exception still only increments `runner_errors`. Do not touch `default_runner`’s argv or the stdout-JSON success check.

## Nice-to-haves

- Extend `scan_static` stats with `hits_by_check`, `hits_by_impact`, `files_by_framework`, and the solc version actually passed to the runner.
- Store `prepare_foundry_deps`’s installed `(repo, tag)` list on `stats` — the prepare loop currently discards that return value.
- Dedupe emitted hits in `scan_static` on `(check, file, contract, description)` before return.
- In `parse_slither_json`, set `StaticHit.contract` from the element whose type is contract, and keep `source_mapping`’s `lines` as a line field, instead of only `elements[0]`.
- Count `subprocess.TimeoutExpired` apart from other `runner_errors` in `scan_static`.

### Triage (in-session GLM, verified against current bytes)
- ACCEPT opt-in hit budget (`select_hits`) - hooks as described (`StaticHit.impact/confidence`, stats dict); default unfiltered return preserved.
- ACCEPT foundry-pinned solc - VERIFIED: `_resolve_solc` sniffs the pragma from `read_text(...)[:800]` only; a caret/late pragma or foundry.toml `solc =` pin selects wrong or none. Fail-soft path unchanged.
- ACCEPT bounded parallel fan-out - VERIFIED: per-file loop is serial and `default_runner` sits on `timeout=180`; grok's design correctly keeps dep-prep serial (forge installs must not race) and merges stats on the main thread.
- DEFER stats extensions (hits_by_check/files_by_framework), hit dedupe, contract/lines parse fields, TimeoutExpired counter.
