# colibri feature review - colibri-bounty/tests/test_config.py

- source: `colibri-bounty/tests/test_config.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `3676409b370e3f4eedfd1a0d3ffe23557da5f6a0b5dd5870db65351f338a2a93`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0444 (in=2772 out=6482)

## grok-4.7 output (verbatim)

## What this module does
This suite locks the offline corpus locator and its sqlite ledger: `BOUNTY_CORPUS_ROOT` beats `config.json` and `DEFAULT_CORPUS_ROOT`, valid-but-unusable JSON falls back instead of crashing, `ensure_dirs` materializes `SUBDIRS` idempotently, and `db.connect` creates `solodit_findings`, `github_repos`, and `sync_runs`. Callers only observe a `Path` and a set of table names, so a replay cannot tell which resolution tier won or which schema text produced the file. `config.PACKAGE_DIR`, `config.ENV_VAR`, and `db.SCHEMA` are public and unused here.

## Suggested add-ons
### Resolution receipt (source + fallback reason)
- **Value:** High
- **Effort:** S
- **What:** When the corpus path is resolved, also return which tier won (`ENV_VAR`, `PROJECT_DIR`/`config.json`, or `DEFAULT_CORPUS_ROOT`) and, on the malformed-JSON path, a reason code for “not an object” vs “`corpus_root` not a string”. Keep returning the same `Path` and keep the non-raising fallback.
- **Why it helps the user:** Precision/recall is only like-for-like if the run discloses which corpus it measured. An env override, a present-but-ignored `config.json`, and the shipped default currently collapse to a bare path, so a wrong-root replay is indistinguishable from the `E:/bounty-corpus` baseline — the same denominator mix-up this funnel already refuses to hide between agent-tier and union figures.
- **How:** Extend `config.corpus_root()` (read the override name from `config.ENV_VAR`; do not hardcode a second string) to attach a small record beside the `Path` that `config.db_path()` already derives. Do not change the fallback `test_malformed_but_valid_json_config_falls_back` locks: still equal `config.DEFAULT_CORPUS_ROOT`, just no longer silent about why.

### Schema identity stamped at open
- **Value:** Med
- **Effort:** S
- **What:** Give `db.SCHEMA` a stable id (hash or integer generation) and record it when `db.connect` creates or opens `corpus.db`, so a later replay can cite the schema that backed `solodit_findings` / `github_repos` / `sync_runs`.
- **Why it helps the user:** Table-name presence is not a denominator. Two `corpus.db` files can share those three names and still differ in columns; a cited schema id keeps an old corpus from being scored as if it were this checkout’s ledger, without a migration framework or a new dependency.
- **How:** Extend `db.SCHEMA` with a version constant and have `db.connect` set `PRAGMA user_version` (stdlib sqlite only) on the connection `test_connect_creates_schema` already opens. Leave create-if-missing behavior as it is; do not invent a migrator.

## Nice-to-haves
- Include `config.PACKAGE_DIR` next to `config.PROJECT_DIR` on the resolution receipt so a relocated checkout is visible in the same record.
- Extend `config.ensure_dirs` to report created vs already-present per `config.SUBDIRS` entry; the second call must stay a no-op, not an error.
- Optional explicit root on `config.corpus_root` / `config.db_path`, mirroring the root argument `config.ensure_dirs` already takes, so a side-by-side offline compare does not mutate `config.ENV_VAR`.

- ACCEPT resolution receipt test-side (tier won + fallback reason code; malformed-JSON fallback assert unchanged) - test-side twin of config.py's stamp; cited test names verified.
- ACCEPT schema identity stamped at open (PRAGMA user_version, no migrator) - twin of db.py's shape-check suggestion; table-name presence is not a denominator.
- DEFER 3 nice-to-haves (PACKAGE_DIR on receipt, created-vs-present per subdir, explicit root args).
