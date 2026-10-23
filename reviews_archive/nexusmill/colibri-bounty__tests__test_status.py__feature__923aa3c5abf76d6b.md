# colibri feature review - colibri-bounty/tests/test_status.py

- source: `colibri-bounty/tests/test_status.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `923aa3c5abf76d6b9579412fb6cb463cddcece4b8ed0ed348f6e8d8b15fa03bb`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0407 (in=2857 out=5830)

## grok-4.7 output (verbatim)

## What this module does
This pytest module is the regression net for the offline corpus-status path: `seeded_conn` builds a throwaway sqlite DB (two Solodit rows, one C4 and one Sherlock repo, one finished sync run) and the tests check `status.corpus_status` counts, `render_md` / `write_status_md`, and that every `cli.ORGS` subdir is a key `config.ensure_dirs` actually returns. That last test locks a past CLI KeyError where a command name was mapped to a subdir the dirs dict never had. It does not call the CLI command functions, config path helpers, `db.SCHEMA`, or the status label/mirror constants.

## Suggested add-ons
1. Value: High. Effort: S. What: Extend the markdown contract so every kind `corpus_status` reports is labeled from `status.KIND_LABELS`, and every org in `status.MIRRORS` that the seed covers appears in the written report — not only the substrings `"49987"` and `"code-423n4"`. Why it helps the user: this file is the operator-facing denominator report before any contest spend; a dropped kind or mirror still passes today and would under-count a corpus the funnel treats as like-for-like. How: extend `test_render_and_write_status_md`; assert against `status.KIND_LABELS` and `status.MIRRORS` on the string from `status.render_md` and the file from `status.write_status_md`, using the c4/sherlock rows already inserted by `seeded_conn`.

2. Value: High. Effort: M. What: Drive `cli.cmd_status` and `cli.main` against the same tmp corpus `test_cli_org_dirs_resolve` already points at `BOUNTY_CORPUS_ROOT`, and assert the figures match `status.corpus_status`. Add one offline `cli.cmd_replay` case on that tmp tree that expects a visible failure when there is nothing to measure — not an empty success. Why it helps the user: the only CLI test is subdir-key resolution; status and replay are how denominators and replay results are actually invoked, and an incomplete measurement must stay visible (transport/setup errors propagate, they are not turned into a silent all-NO). How: new test next to `test_cli_org_dirs_resolve`, monkeypatch only `config.ENV_VAR`, call `cli.cmd_status` and `cli.main`, compare to `status.corpus_status` / `status.render_md`; call `cli.cmd_replay` on the tmp path with no contest fixtures and assert the error surfaces. No network, no live-contest path, no merging of agent-tier and union figures.

3. Value: Med. Effort: S. What: Lock path and schema contracts the status counts depend on: `config.corpus_root` and `config.db_path` follow `config.ENV_VAR` and otherwise `config.DEFAULT_CORPUS_ROOT`, and `db.SCHEMA` still contains the columns `seeded_conn` inserts and `corpus_status` counts. Why it helps the user: a wrong root or a drifted table silently measures a different corpus; the suite currently monkeypatches the env var by string and never checks `db.SCHEMA`. How: new test using `config.corpus_root`, `config.db_path`, `config.ENV_VAR`, `config.DEFAULT_CORPUS_ROOT`, `config.PACKAGE_DIR` / `config.PROJECT_DIR` only as anchors that `config.ensure_dirs` stays under the resolved root; parse `db.SCHEMA` via `db.connect` and compare to the insert columns in `seeded_conn`.

## Nice-to-haves
- Empty DB through `status.corpus_status` + `status.render_md`: every `status.KIND_LABELS` key still renders an explicit zero, not an omitted row.
- Assert the seeded `sync_runs` fields besides `total_results` (`status`, `pages_done`) if `status.corpus_status` already returns them.
- `cli.cmd_solodit` and `cli.cmd_mirrors`: argv handling plus missing-root refusal only — no network, stdlib monkeypatch as in `test_cli_org_dirs_resolve`.
- Second `status.write_status_md` to the same path is idempotent (same bytes, still one file).

- ACCEPT full KIND_LABELS/MIRRORS coverage in the markdown contract - VERIFIED: asserts are substring-only ("49987", "code-423n4"); a dropped kind/mirror passes today.
- ACCEPT cli.cmd_status/main driven against the tmp corpus + offline cmd_replay visible-failure case - the only CLI test today is subdir resolution.
- ACCEPT path+schema contract locks (corpus_root/db_path precedence, SCHEMA columns vs seed inserts).
- DEFER 4 nice-to-haves (empty-DB explicit zeros, extra sync_runs fields, cmd_solodit/mirrors argv, idempotent rewrite).
