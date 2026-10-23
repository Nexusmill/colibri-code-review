# colibri feature review - colibri-bounty/tests/test_scanner.py

- source: `colibri-bounty/tests/test_scanner.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `6ec4fdaf76a20de3a46d2f5dfd6098e51ac45120c523c82386bb39fdc65ca83e`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0463 (in=2320 out=6951)

## grok-4.7 output (verbatim)

## What this module does
This suite is the only pytest check on `scanner` and `truth`: `judged()` builds in-memory `JudgedFinding` rows, `test_stub_scans_nothing` asserts `StubScanner` is an empty named no-op, and `test_oracle_emits_paid_truth_back` asserts `OracleScanner.scan` replays two titles and drops one hardcoded Low. It never references `ScanFinding`, the severity sets, title-key helpers, or the load/select path, so a green run only locks that one literal High/Medium filter.

## Suggested add-ons
**Paid-set oracle contract**
Value: High
Effort: S
What: Drive the oracle from `truth.SEVERITIES` / `truth.PAID` / `truth.STOP` instead of the literal `("High", "Medium")` and a single Low drop. Every PAID severity is emitted with its title unchanged; every non-PAID severity is absent.
Why: The file's only behavioral claim is that the oracle emits paid truth. A hardcoded pair can drift from `truth.PAID` and still pass, so the pre-spend check would be using a different severity denominator than the funnel.
How: Extend `judged()` and `test_oracle_emits_paid_truth_back`. One `JudgedFinding` per `truth.SEVERITIES` entry, then `scanner.OracleScanner(fs).scan`; keep titles in `truth.PAID`, assert absence for `truth.STOP` and any severity not in `truth.PAID`.

**ScanFinding identity and path-independence**
Value: Med
Effort: S
What: Assert `scan()` yields `scanner.ScanFinding`, and that Stub and Oracle results do not change when `tmp_path` contains an unrelated file versus when it is empty.
Why: Later tiers consume `ScanFinding`, but this file only reads `.title` and `.severity`, so a duck-typed stand-in stays green. Path-independence is what keeps these two scanners an offline replay rather than a scan of whatever directory was passed in.
How: In `test_stub_scans_nothing` and `test_oracle_emits_paid_truth_back`, `isinstance(f, scanner.ScanFinding)` and compare `scan(tmp_path)` with `scan` of a second path that holds a dummy file. Read existing `ScanFinding` fields off the class; do not add fields, I/O, or a scanner.

**Offline truth-ingest round-trip**
Value: High
Effort: M
What: A `tmp_path` fixture through `parse_judging_issues` → `valid_findings` → `load_truth`, then into `OracleScanner`, including at least one row `valid_findings` drops, so the paid replay and the valid denominator are the same objects.
Why: The oracle is fed hand-built `JudgedFinding`s. Parse, valid-filter, or load can change the contest set and this file still passes, which is a false green on the denominator later matching uses.
How: New test beside `test_oracle_emits_paid_truth_back`, calling `truth.parse_judging_issues`, `truth.valid_findings`, and `truth.load_truth` with the signatures they already have. Synthetic file under `tmp_path` only — not `E:/bounty-corpus`, no new dependencies. Paid subset of the loaded list must match `OracleScanner` on that list.

## Nice-to-haves
- Snapshot `truth.select_contests` on a tiny in-memory contest list so a later S2 v2 target change cannot move the measured set without a failing test; do not add a selector.
- Pin `truth.norm_tokens` and `truth.title_key` on case, punctuation, and whitespace variants those functions already accept; no matcher or dedup policy (S5 is already docketed).
- `OracleScanner([])` and a list of only non-PAID severities both `scan` to `[]`, so the empty-paid edge is explicit.
- Assert `StubScanner.name` and `OracleScanner.name` stay distinct stable tier keys (`"stub"` / `"oracle"`).

- ACCEPT paid-set oracle contract driven from truth.SEVERITIES/PAID/STOP - VERIFIED: the literal ("High","Medium") pair + single Low drop can drift from truth.PAID and still pass.
- ACCEPT ScanFinding isinstance + path-independence asserts - VERIFIED: only .title/.severity are read today.
- ACCEPT offline truth-ingest round-trip (parse -> valid -> load -> oracle, incl. a dropped row).
- DEFER 4 nice-to-haves (select_contests snapshot, norm_tokens/title_key pins, empty-paid edge, name-key stability).
