# colibri feature review - colibri-bounty/tests/test_mirrors.py

- source: `colibri-bounty/tests/test_mirrors.py`
- model: grok-4.7 via api.x.ai (external second opinion, OFF-LADDER - does not count toward the three-model lock)
- sha256: `d3391b1669f20c712385762565d60c7182751a0132267e41bc2952484d8293de`
- date: 2026-10-21
- mode: feature (the SUGGEST pass - owner standing order 2026-10-13)
- context pack: shared funnel/doctrine pack + AST-derived symbols + consumers + coverage gaps (tests) + live deferred/remediation manifest rows + run-1 backlog injected as already-planned + RSI ruleset (0 active)
- prompt: colibri/feature@2 (langfuse)
- cost: ~$0.0446 (in=2607 out=6572)

## grok-4.7 output (verbatim)

## What this module does
This suite locks the offline git contract of `mirrors.sync_mirror`: a local repo is cloned on the first call and fast-forwarded on the second, with dest file bytes matching the source commit. A missing remote returns the fail-soft `"error"` string rather than raising. `mirrors.sync_all`, `mirrors.DEFAULT_MIRRORS`, and `mirrors.default_runner` are never called.

## Suggested add-ons
### Disclosed per-mirror sync receipt
- Value: High
- Effort: S
- What: A `sync_all` result that records, per mirror, the existing `sync_mirror` status (`cloned` / `updated` / `error`) plus the dest HEAD sha.
- Why it helps the user: Replay precision/recall is only like-for-like if the run can cite which mirror revision was measured. Today a successful sync leaves no revision the honest table can disclose, so two runs can drift under the same status word.
- How: Extend `mirrors.sync_all` to walk `mirrors.DEFAULT_MIRRORS`, call `mirrors.sync_mirror` unchanged (keep the string the tests assert), and have `mirrors.default_runner` run `git rev-parse HEAD` in the dest after a non-error sync. Fold `{name: {status, rev}}` as the `sync_all` return; do not merge this into matcher denominators.

### Visible fail-soft error detail
- Value: Med
- Effort: S
- What: On the `"error"` path, keep the status string and attach the git stderr (and the source url) on that mirror's receipt entry.
- Why it helps the user: `test_error_result_on_bad_url` only proves the token. An operator replaying against `E:/bounty-corpus` cannot tell a missing path from a non-repo, so a partial corpus can sit under a bare `"error"` and quietly shrink the truth set.
- How: Extend `mirrors.sync_mirror` to stash stderr from the `mirrors.default_runner` invocation it already uses, and surface it only on the `mirrors.sync_all` receipt. Do not raise — the fail-soft string contract stays.

### Offline root override for the batch entry point
- Value: Med
- Effort: S
- What: Let `sync_all` accept a local root (or per-name path map) so every default mirror can be satisfied from a filesystem path, the same way this suite passes a local repo to `sync_mirror`.
- Why it helps the user: The single-mirror path is already offline; the batch path is the one a measurement run will call. An override avoids editing `DEFAULT_MIRRORS` and avoids any fetch when the corpus is already on disk.
- How: Add an optional `roots` argument on `mirrors.sync_all` that replaces each `mirrors.DEFAULT_MIRRORS` url before the existing `mirrors.sync_mirror` call. No new deps; remote urls remain the default when `roots` is omitted.

## Nice-to-haves
- Distinct `"current"` status from `mirrors.sync_mirror` when the second sync is a no-op, so a re-run is not logged as a corpus change.
- Plumb optional `git clone` args (`--single-branch`) through `mirrors.default_runner` for large Solodit trees; default invocation unchanged.
- Point the suite's `git()` helper at `mirrors.default_runner` so test and production share one git invocation path.

- ACCEPT per-mirror sync receipt (status + dest HEAD sha from sync_all) - test-side twin of mirrors.py manifest suggestion; sync_all/DEFAULT_MIRRORS/default_runner never called by the suite today (verified).
- ACCEPT fail-soft error detail (git stderr on the receipt, string contract unchanged).
- ACCEPT offline root override for the batch entry point (roots arg replacing urls; no fetch when corpus on disk).
- DEFER 3 nice-to-haves (distinct no-op status, clone args plumbing, shared git runner).
