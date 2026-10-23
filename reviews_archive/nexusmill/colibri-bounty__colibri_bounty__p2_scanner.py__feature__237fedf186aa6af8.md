# colibri feature review - colibri-bounty/colibri_bounty/p2_scanner.py

- source: `colibri-bounty/colibri_bounty/p2_scanner.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `237fedf186aa6af86654ea617a42d89fc1affe9de479fab6629b7d27b46f575d`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0609 (in=4414 out=8671)

## grok-4.7 output (verbatim)

## What this module does

`P2Scanner` and `P2XScanner` are the P2 replay adapters: they run fail-soft Slither (`p2_static.scan_static`), slice the tree into per-file or cross-file review units, then spend a capped LLM budget on `p2_llm.review_unit` plus `p2_llm.verify_unit`. They dedup with `title_key`, return `ScanFinding`s through the P1 scanner interface, and stash a side-channel `last_stats` (including `budget_stopped`) so the harness can score a partial pass without aborting the contest.

## Suggested add-ons

**Partial-scan coverage manifest**
Value: High. Effort: S.
What: Record a machine-readable unit ledger on `last_stats`: units enumerated, reviewed, remaining, unreadable, and truncated — not only the boolean `budget_stopped`.
Why it helps the user: A `BudgetExceeded` returns partial findings that the harness will otherwise score as a full contest. The doctrine needs that incomplete denominator visible and like-for-like; today the operator cannot say which files the precision/recall number actually covers.
How: In both `P2Scanner.scan` and `P2XScanner.scan`, snapshot the planned unit list before the loop (the `rglob("*.sol")` walk filtered by `p2_static.SKIP_DIRS`, or the list from `p2_units.cluster_files`). Append each finished unit id as you go. In the `p2_llm.BudgetExceeded` handler, set `units_remaining` to the tail and keep returning partial findings. Count `OSError` reads and `max_source_chars` cuts in the same dict.

**Spend preflight (no client)**
Value: High. Effort: S.
What: A no-LLM estimate of review units, truncation, and call range before `client_factory` is invoked.
Why it helps the user: This funnel exists to decide whether a contest is worth paid spend. `scan` always constructs `p2_llm.OpenRouterClient` and burns budget in alphabetical / cluster order; the operator cannot see "N units, between N and 2N calls, K already over `max_source_chars`" without paying.
How: Add `P2Scanner.estimate` and `P2XScanner.estimate` that reuse the same enumeration as `scan` (`SKIP_DIRS`, `installed_versions` unused, `p2_units.cluster_files(..., max_chars=self.unit_chars)`, `unit_chars` / `max_source_chars` checks) and do not call `client_factory`, `review_unit`, or `verify_unit`. Report `units`, `call_range = [len(units), 2*len(units)]` (verify runs only when `cands` is non-empty), truncated-unit count, and static-hit counts per unit from an optional already-built `by_file`. Leave `scan` as the only spending path.

**P2X cluster attribution**
Value: High. Effort: S.
What: Keep cross-file findings attached to the cluster that produced them, instead of collapsing every hit onto `unit[0]`.
Why it helps the user: `P2XScanner` exists so integration bugs are reviewed inside one unit, but the `ScanFinding` the harness matches and the operator inspects is filed under whichever file `cluster_files` put first. A real bug in file 3 of "A + B + C" is indistinguishable from a bug in A, so P2X recall cannot be audited file-by-file.
How: At the `ScanFinding(...)` append in `P2XScanner.scan`, add a helper that picks `path` only when exactly one member of `unit` is named in `c["title"]` or `c["detail"]`; otherwise keep `unit[0]`. Always store `title_key(c["title"]) -> [f.name for f in unit]` (and the already-built `unit_name`) on `last_stats`. Do not change `title_key` dedup or the `ScanFinding` fields the matcher already consumes.

## Nice-to-haves

- Opt-in static-hit-density unit order in both `scan` loops (default remains sorted / `cluster_files` order), with the policy string copied onto `last_stats`, so a capped budget reviews signal-rich units first without silently shifting historical denominators.
- When `source` is cut at `max_source_chars`, prepend a one-line truncation marker before `review_unit` / `verify_unit` and count cuts in `last_stats`, so verify is not judging a head-truncated file as the whole contract.
- Wrap the `context_builder(code_dir)` call in both scanners fail-soft: on error, record `context_error` and continue with `context_block=""`, matching the module's fail-soft-except-spend rule.
- Count basename collisions in the `by_file` join (`Path(h.file).name`) and surface them on `last_stats`, so shared filenames (the F1 absolute-path workaround) are a disclosed measurement caveat rather than a silent hit merge.
- Count `title_key` suppressions (`k in seen_keys`) separately from verified candidates, so in-scanner dedup is visible before S5 runs the same key again.

- ACCEPT partial-scan coverage manifest (unit ledger on last_stats) - VERIFIED: BudgetExceeded returns partials with only the boolean budget_stopped; which files the P/R number covers is invisible.
- ACCEPT spend preflight (estimate, no client) - VERIFIED: scan constructs the paid client before any enumeration is visible to the operator.
- ACCEPT P2X cluster attribution - VERIFIED: every ScanFinding carries path=str(unit[0]) regardless of which cluster member the finding names.
- DEFER 5 nice-to-haves (hit-density order opt-in, truncation marker, context_builder fail-soft wrap [a raising builder crashes scan today], basename-collision count, title_key suppression count).
