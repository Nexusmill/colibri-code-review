# Colibri review — adversary-gate/gate_selftest.py (bug)

- source: `C:\Users\User\source\repos\Tools\adversary-gate\gate_selftest.py`
- model: claude-fable-5-1 (in-session Phase-3 gate over the external raw z-ai/glm-5.3-flash review, `.colibri_reviews/_external_raw/tools__gate_selftest.py__glm-5.3-flash.md`, run 2026-09-02 at sha `ed518ea3ce67f8fa…`)
- sha256: `db37e203e0f86cd5861a267dc0828950f676f81b057be14e48c27e6b68816a79` (current bytes at dispatch, 2026-09-05; CHANGED since the raw: a72b051 (2026-09-02, the 8-round gate hardening) and later gate commits.)
- date: 2026-09-05
- mode: bug
- context pack: current bytes read end to end; jCodemunch/call-site lookups on this repo; `git log -S` for the fix commits cited below; the raw review; the repo's existing `.colibri_reviews/_manifest.json` (no prior bug-mode record for this file). Every external finding re-traced against the cited lines (Phase 3): CONFIRMED / PLAUSIBLE kept, fixed-since-raw ones recorded verified-stale with their commit, refuted ones listed with the reason (G35: neither class is ever re-fixed).

## Verdict
The MEDIUM false-PASS was closed in a72b051; the two LOWs are hygiene.

## Verified-stale external findings (fixed on disk — G35: never re-fix)
- MEDIUM #1 test 15b could false-PASS on a refused commit — FIXED a72b051: `post_baseline_commit_ok` asserts the cleared commit landed before `record`/`push` (line 246-249), with a comment naming exactly this failure.

## Bugs & vulnerabilities (still open on current bytes)
**[LOW] Hook scripts written by the tests are never made executable — CONFIRMED (false-FAIL on POSIX, not false-pass)** - `line 227-229` and the other hook writes
- On Linux/macOS git skips the non-executable hooks and `hook_blocks_commit` / `push_guard_refuses_unnotarized` fail loudly. The suite is Windows-first by design; `os.chmod(path, 0o755)` after each write would make it portable and exercise the arming path.

**[LOW] Throwaway repos are never removed — CONFIRMED** - `line 43, 224`
- `mkdtemp` twice, no `rmtree` in a `finally`; `SystemExit` from `git()` abandons them mid-run.
