# colibri feature review - colibri-bounty/colibri_bounty/config.py

- source: `colibri-bounty/colibri_bounty/config.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `0ab656980c6c5081be4859f4d387dbb16fdc6da21da460dc46c3d9d83f9a8ae4`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0317 (in=2582 out=4418)

## grok-4.7 output (verbatim)

## What this module does
Shared path resolution for every funnel tier: `corpus_root()` picks the corpus by `BOUNTY_CORPUS_ROOT`, then `config.json`'s `corpus_root`, then `DEFAULT_CORPUS_ROOT`, and fails soft on a missing or misshapen config. `ensure_dirs()` materializes the fixed `SUBDIRS` tree (including `mirrors`); `db_path()` points at `corpus.db` under that root. Callers get a path only — not which source won, and not whether the tree or db is actually there.

## Suggested add-ons
- **Value:** High. **Effort:** S. **What:** A resolution stamp (`path` + winning source: env / config.json / default) that status and S5 can attach to every measurement row. **Why it helps the user:** Honest, like-for-like denominators require knowing which corpus a 26.7% or 27.1% figure was scored against; today an env override and the E: default are indistinguishable, so two runs can be compared as if they were the same corpus. **How:** Add `corpus_resolution()` beside `corpus_root()`, reusing `ENV_VAR`, `_config_file_root()`, and `DEFAULT_CORPUS_ROOT`; keep `corpus_root()` as a thin wrapper so existing callers stay stable. Do not merge agent-tier and union figures — only stamp the root identity on each.

- **Value:** High. **Effort:** S. **What:** A read-only corpus readiness probe (root present, each `SUBDIRS` entry present, `corpus.db` present) that never creates directories and never raises. **Why it helps the user:** Fail-soft tiers plus a mkdir-on-use `ensure_dirs()` can turn a missing `sherlock-issues` tree into an empty denominator that still looks like a completed replay. A probe lets status disclose an incomplete corpus before any tier runs, without hiding a failed measurement. **How:** New `corpus_probe(root=None)` next to `ensure_dirs()` and `db_path()`, checking `is_dir` / `is_file` only. Status (already a consumer of this module) renders the dict; tiers keep calling `ensure_dirs()` only when they intend to create the tree.

- **Value:** Med. **Effort:** S. **What:** Optional dump-directory resolution with the same precedence and fallback style as the corpus root, defaulting under the resolved corpus root. **Why it helps the user:** This module is the shared place for corpus root, mirrors, and dump locations, but only root, fixed subdirs, and `corpus.db` are resolved — S4/S5 dump paths would otherwise drift per tier and break offline replay comparability. **How:** Generalize `_config_file_root()` into a small optional-key read (still return `None` on wrong shape, per the existing fallback) and add `dump_dir(root=None)` parallel to `db_path()`. No new env-var family and no new dependency; absent key means `<corpus_root>/dumps`.

## Nice-to-haves
- Sibling of `_config_file_root()` that reports why config was skipped (missing file, invalid JSON, non-dict, empty `corpus_root`) for status, without changing the fallback.
- `mirrors_dir()` accessor next to `db_path()` so callers stop indexing `SUBDIRS` by hand.
- `ensure_dirs()` notes created vs already-present for funnel logs; keep `exist_ok=True`.
- Process-lifetime memo of `corpus_resolution()` so one run cannot change denominator if the environment is mutated mid-process.

- ACCEPT resolution stamp (corpus_root provenance) - VERIFIED: corpus_root() is env > config.json > default and returns a bare Path; ENV_VAR/_config_file_root/DEFAULT_CORPUS_ROOT hooks exact; two corpora are indistinguishable in saved runs.
- ACCEPT read-only corpus_probe (never mkdir/raise) - VERIFIED: ensure_dirs() mkdirs on every call; a missing sherlock-issues tree silently yields empty denominators.
- ACCEPT dump_dir resolution (Med) - hooks exact (_config_file_root generalization).
- DEFER 4 nice-to-haves (skip-reason sibling, mirrors_dir accessor, created-vs-present note, process-lifetime memo).
