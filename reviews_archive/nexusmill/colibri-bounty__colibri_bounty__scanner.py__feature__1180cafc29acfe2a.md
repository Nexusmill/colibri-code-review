# colibri feature review - colibri-bounty/colibri_bounty/scanner.py

- source: `colibri-bounty/colibri_bounty/scanner.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `1180cafc29acfe2a5ee53f439608cfc5d1e2dbc70746bc9931c1366f6fa15f40`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0579 (in=2490 out=8822)

## grok-4.7 output (verbatim)

## What this module does

This is the shared emit contract for the offline replay harness: every tier returns `list[ScanFinding]` from `scan(code_dir)`, `StubScanner` is the empty floor, and `OracleScanner` replays `valid_findings(self.truth)` through that same record so the harness can prove precision=recall=1.0. `ScanFinding` carries only title, severity, detail, and path; scanner identity stays on the scanner object and is dropped once `scan` returns. The oracle mapping copies title, severity, and `JudgedFinding.body` into detail, and leaves path blank.

## Suggested add-ons

### Provenance stamped at emit time
- Value: High
- Effort: S
- What: Optional `scanner`, `tier`, and `contest_id` on `ScanFinding`, filled when a finding is emitted, defaulting to empty so existing constructors and tests keep working.
- Why it helps the user: Unioned lists cannot currently say which tier or contest a row came from, so agent-tier and union figures have to be kept apart by list identity alone. Stamping at emit time keeps those denominators separable after concatenation and lets a pooled corpus run still attribute a hit to a contest.
- How: Add the three fields to `ScanFinding`. Set `scanner=self.name` inside `StubScanner.scan` and in the `OracleScanner.scan` loop over `valid_findings`. Add an optional `contest_id: str = ""` (and `tier: str = ""`) on `StubScanner` and `OracleScanner`, copied onto each finding in those two `scan` methods. `colibri_bounty/s5.py` reads `tier` at union time; it does not infer tier from list position, and the fixed agent>t5>poc priority stays where it is.

### Visible tier disposition, separate from the finding list
- Value: High
- Effort: M
- What: A `status` on the scanner (`ok`, `floor`, `skipped`, `degraded`) set by `scan`, meaning intentional disposition only. Exceptions still propagate; nothing is caught or turned into an empty list.
- Why it helps the user: Fail-soft tiers and a real zero both surface as `[]` today, so a skipped tier can be scored as a measured clean contest and move precision/recall before any live spend. A visible status keeps an incomplete tier out of the denominator without hiding it.
- How: Add `status: str = "ok"` on `StubScanner` and `OracleScanner`. `StubScanner.scan` sets `self.status = "floor"` before returning `[]`. `OracleScanner.scan` sets `self.status = "ok"`. Do not wrap `scan` in try/except. The replay runner (pinned by `tests/test_replay_runner.py`) and metrics read `status` after `scan` and exclude `skipped`/`degraded` from scored denominators while still reporting them.

### One constructor for the oracle proof
- Value: Med
- Effort: S
- What: `ScanFinding.from_judged(...)` as the only truth-to-scanner mapping, so new record fields cannot be applied in one scanner and forgotten in the plumbing proof.
- Why it helps the user: The oracle is the check that the harness scores precision=recall=1.0. The mapping is an inline constructor in `OracleScanner.scan` today; the next field added to `ScanFinding` will silently not round-trip and the 1.0 pin will either fail late or, worse, keep passing while real scanners fill fields the oracle never exercises.
- How: Add `ScanFinding.from_judged(f, *, scanner="", tier="", contest_id="")` next to the dataclass, mapping `title`, `severity`, and `body` to detail (path stays blank unless `JudgedFinding` already has a location attribute, in which case copy it with `getattr`). Replace the list comprehension in `OracleScanner.scan` with that constructor, passing `self.name` and the scanner's tier/contest fields.

## Nice-to-haves

- A stdlib `typing.Protocol` (`name` + `scan(code_dir) -> list[ScanFinding]`) in this module, already satisfied by `StubScanner` and `OracleScanner`, so new tiers type-check against the plug without a new dependency.
- A `fan_out(scanners, code_dir)` helper here that concatenates `scan` results and fills an empty `scanner` from each scanner's `name`, for S1 fan-out without owning any concrete scanner.
- An optional `note: str = ""` on `StubScanner` and `OracleScanner`, default empty, for the offline/no-spend line so disclosure stays on the scanner object and the paid channel stays opt-in.

- ACCEPT provenance stamped at emit time (scanner/tier/contest_id default-empty fields) - VERIFIED: ScanFinding carries none of the three; identity drops at scan() return; s5 attributes tier from the per_tier dict key, not the finding.
- ACCEPT visible tier disposition status (ok/floor/skipped/degraded; no try/except wrap, exceptions still propagate) - same []-ambiguity class as p2_scanner/replay_runner findings; coherent fix at the contract root.
- ACCEPT ScanFinding.from_judged single oracle mapping (inline comprehension today; next field added risks silently not round-tripping the 1.0 pin).
- DEFER 3 nice-to-haves (Protocol, fan_out helper, scanner note field).
