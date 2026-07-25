# BUG review: _git_restore.py

- source: `C:\Users\User\source\repos\Nexusmill\_git_restore.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-19 21:02
- tokens: in 641 / out 980
- est cost: $0.0166

---

## Verdict
Low blast radius (no untrusted input, no injection surface since all args are literals), but it has real correctness defects: it proceeds to read and syntax-check the file even if `git checkout` failed, silently reporting on the old (buggy) version. Not safe to ship as an automated check without a return-code gate.

## Bugs & vulnerabilities
**[HIGH] Continues after failed git checkout — validates the wrong file** - `line 5-8`
- What: `r.returncode` is only printed, never checked. If checkout fails (path not in index, repo locked by `index.lock`, dirty-tree refusal, wrong path), execution falls through to reading whatever version of `__init__.py` was already on disk.
- Trigger: e.g. path typo, concurrent git operation holding `.git/index.lock`, or the file being untracked.
- Impact: Lines 8-14 report line count, `EDGE_INLAY` presence, and `SYNTAX_OK` for the stale file — a false "restore succeeded" signal, exactly the silent failure this script is meant to guard against.
- Fix: `if r.returncode != 0: sys.exit(f"checkout failed: {r.stderr.strip()}")` before line 7.

**[MEDIUM] Unclosed file handle** - `line 8`
- What: `open(p, encoding="utf-8")` is never closed; relies on CPython refcount GC.
- Trigger: always; especially relevant since line 5 just modified the file via git — on Windows, lingering handles can block subsequent git operations on the same path in some cases.
- Impact: resource leak; flaky behavior under PyPy or repeated invocations.
- Fix: `with open(p, encoding="utf-8") as f: n = sum(1 for _ in f)`

**[MEDIUM] File-not-found crashes with unhandled traceback** - `line 8`
- What: If the checkout (or path) is wrong so `p` doesn't exist, `open()` raises `FileNotFoundError` and the script dies before printing any diagnostic.
- Trigger: missing/renamed `PatternSkin/__init__.py`.
- Impact: opaque crash instead of a "restore failed" message.
- Fix: check `os.path.exists(p)` or wrap in try/except with a clear message.

**[LOW] Substring sanity check is fragile** - `line 11`
- What: `"fcen.mean(0)" in t` matches regardless of context — comments, dead code, or a renamed-but-equivalent call (`fcen . mean(0)`, `np.mean(0)` rewrite) all give misleading results. `"EDGE_INLAY" in t` also matches if it appears only in a comment or string literal.
- Trigger: refactorings or comments mentioning these tokens.
- Impact: false positive/negative on "old buggy version restored."
- Fix: use a regex on actual code (e.g. strip comments first) or compare against the expected blob hash (`git rev-parse HEAD:PatternSkin/__init__.py` vs file hash).

**[LOW] Hardcoded machine-specific paths** - `line 2-3`
- What: Absolute paths to git.exe and a user-specific repo; fails outright on any other machine/CI.
- Fix: locate git via `shutil.which("git")` and take repo path from an argument/env var.

## Missing safeguards
- `check=True`-style enforcement on `subprocess.run` (or explicit rc handling) for line 5.
- No timeout on `subprocess.run` — a hung git (credential prompt suppressed by `capture_output`, lock wait) blocks forever; add `timeout=`.
- No verification that the restored content matches the intended revision (e.g. compare `git diff` emptiness or blob hash) — currently "restored" is inferred from loose substring tests.
- No test/assertion on the sanity output: results are printed, never asserted, so automation can't fail on them.
- No handling of the repo being mid-merge/rebase or the file having local modifications that checkout would refuse or clobber — the script silently discards uncommitted changes to `PatternSkin/__init__.py` with no backup or confirmation.