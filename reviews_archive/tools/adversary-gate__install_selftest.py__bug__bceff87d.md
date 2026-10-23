# Colibri review — adversary-gate/install_selftest.py (bug)

- source: `C:\Users\User\source\repos\Tools\adversary-gate\install_selftest.py`
- model: claude-fable-5-1 (in-session Phase-3 gate over the external raw z-ai/glm-5.3-flash review, `.colibri_reviews/_external_raw/tools__install_selftest.py__glm-5.3-flash.md`, run 2026-09-02 at sha `bceff87d63b76ebc…`)
- sha256: `bceff87d63b76ebc4c5cea3ce25129846ae1977c00ee27895bee17d835b257c5` (current bytes at dispatch, 2026-09-05; unchanged since the raw.)
- date: 2026-09-05
- mode: bug
- context pack: current bytes read end to end; jCodemunch/call-site lookups on this repo; `git log -S` for the fix commits cited below; the raw review; the repo's existing `.colibri_reviews/_manifest.json` (no prior bug-mode record for this file). Every external finding re-traced against the cited lines (Phase 3): CONFIRMED / PLAUSIBLE kept, fixed-since-raw ones recorded verified-stale with their commit, refuted ones listed with the reason (G35: neither class is ever re-fixed).

## Verdict
Clean: the single external MEDIUM rests on a premise the installer disproves.

## Refuted external findings
- MEDIUM `shim_executable_posix` "asserts working-tree mode that `update-index --chmod=+x` never sets": the installer ALSO chmods the working-tree shim (`install_gate.py:285`, `os.chmod(dst, 0o755)`), so on POSIX the on-disk file is executable, git runs it, and the `os.access(..., X_OK)` check (line 83-85) is valid. The reviewer's own caveat ("if the installer does chmod the file ... disregard this finding") applies.

## Missing safeguards
- None found beyond the existing canonical-bytes comparisons.
