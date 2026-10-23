# Colibri review — adversary-gate/owner_setup.py (bug)

- source: `C:\Users\User\source\repos\Tools\adversary-gate\owner_setup.py`
- model: claude-fable-5-1 (in-session Phase-3 gate over the external raw z-ai/glm-5.3-flash review, `.colibri_reviews/_external_raw/tools__owner_setup.py__glm-5.3-flash.md`, run 2026-09-02 at sha `284672f6cff40283…`)
- sha256: `284672f6cff40283c8ceb45d18560ab76c63001c345c9e40d349d617c89e232d` (current bytes at dispatch, 2026-09-05; unchanged since the raw.)
- date: 2026-09-05
- mode: bug
- context pack: current bytes read end to end; jCodemunch/call-site lookups on this repo; `git log -S` for the fix commits cited below; the raw review; the repo's existing `.colibri_reviews/_manifest.json` (no prior bug-mode record for this file). Every external finding re-traced against the cited lines (Phase 3): CONFIRMED / PLAUSIBLE kept, fixed-since-raw ones recorded verified-stale with their commit, refuted ones listed with the reason (G35: neither class is ever re-fixed).

## Verdict
Owner-run one-shot script; one real robustness gap (a missing `gh`/`git` crashes the push loop instead of reporting FAIL per repo).

**[MEDIUM] Uncaught `FileNotFoundError` at the two unguarded subprocess sites — CONFIRMED** - `line 150, 156`
- `_gh` (131-140) maps a missing `gh` to rc 127, but the `gh auth refresh` call and the per-repo push loop call `subprocess.run` directly; a missing `gh` or a `GITEXE` that is not at the hardcoded path aborts the script with a traceback after Part A already mutated settings, and the loop's per-repo FAIL reporting never runs. Reuse the `_gh` guard; verify `os.path.isfile(GITEXE)` up front.

**[LOW] The `workflow` scope is never re-verified after the refresh — CONFIRMED** - `line 150-153`
- A refresh that exits 0 but grants nothing (aborted browser step, other account) proceeds to four pushes that fail with the original scope error.

**[LOW] Orphaned `settings.json.tmp` on a failure between write and replace — CONFIRMED** - `line 116-123`
- The re-validate and `os.replace` are unguarded; the `.tmp` is never cleaned up and the crash skips the FAIL messaging. Wrap in `try/except` with cleanup and `return False`.

## Fixed 2026-09-06 (remediation item 9, TDD, gated commit)
- **MEDIUM unguarded subprocess sites - FIXED.** Part B verifies `GITEXE` up front and treats
  `_gh`'s rc 127 as FAIL; the interactive `gh auth refresh` (deliberately NOT routed through
  `_gh`'s capture - it shows a device code) is wrapped for `FileNotFoundError`; each push is
  wrapped for `OSError` and reports a FAIL row instead of aborting the loop.
- **LOW `workflow` scope never re-verified - FIXED.** After a refresh that exits 0, `gh auth
  status` is re-read and Part B fails before any push if the scope is still absent.
- **LOW orphaned `settings.json.tmp` - FIXED.** The write / re-validate / replace is wrapped
  for `(OSError, ValueError)`: the `.tmp` is removed, a FAIL row printed, `False` returned, and
  the original settings.json is untouched.
- Tests: `adversary-gate/owner_setup_selftest.py` - every path redirected (SETTINGS, GUARD,
  GH, GITEXE, PUSHES) so nothing real is touched; fake `gh.cmd` shims with/without the scope;
  `os.replace` patched to raise. **Gate round 1 (grok, 12:02) caught the first cut of this
  selftest as VACUOUS:** every Part B scenario set `GITEXE` to a missing path, so all three
  returned at the new up-front `isfile(GITEXE)` guard and the gh-missing branch, the
  post-refresh re-verify and the per-repo `except OSError` row were never executed - the
  "9/9 PASS" I cited was green for the wrong reason, and the unrefreshed-scope check matched
  the static section header's word "workflow". Rewritten: `GITEXE` is a real runnable file
  (this interpreter) or a real NON-executable file (WinError 193 -> the OSError row) per
  scenario, the gh-missing check asserts the specific message, the unrefreshed check asserts
  the specific post-refresh FAIL text and that no push row was printed. 12 checks, 12/12. The six existing
  adversary-gate selftests (gate 63, guard 148, audit 15, install 38, callmodel 4, docscan 11)
  all pass.
