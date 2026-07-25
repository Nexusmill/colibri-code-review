# BUG review: tools\sync_builds.py

- source: `C:\Users\User\source\repos\Nexusmill\tools\sync_builds.py`
- model: moonshotai/kimi-k3
- reviewed: 2026-07-20 01:14
- tokens: in 2254 / out 1745
- est cost: $0.0329

---

## Verdict
Mostly functional as a drift guard, but not safe to ship as-is: the `--fix` direction is documented backwards relative to what the code actually does, so a user following the docstring can overwrite the good build with the drifted one — the exact failure this tool exists to prevent.

## Bugs & vulnerabilities
**[HIGH] `--fix` direction documented backwards — doc-guided invocation overwrites the wrong tree** - `lines 9-10 vs 105-114`
- What: The docstring says `--fix A>B` copies "asset-forge-user -> asset-forge", but the code for `"A>B"` (line 110-113) does `shutil.copyfile(fa[r], fb[r])` — creator -> user, the exact opposite. `"B>A"` is likewise reversed versus the doc.
- Trigger: Operator reads the usage text, sees drift, runs `python tools/sync_builds.py --fix A>B` intending to push the (correct) user build into the creator build.
- Impact: The drifted/wrong file is copied over the correct one, the tool prints "fixed" and exits 0 — silent destruction of the known-good side with no backup and no confirmation.
- Fix: Make code and docs agree on one convention (e.g. `A>B` = A → B = creator → user), and print the resolved source/destination before copying. Ideally require a `--yes` confirmation or write a `.bak` before overwrite.

**[MEDIUM] `IndexError` crash when `--fix` is the last argument** - `line 78`
- What: `argv[argv.index("--fix") + 1]` raises `IndexError` if the user runs `python tools/sync_builds.py --fix` with no value.
- Trigger: `--fix` as final CLI token.
- Impact: Traceback instead of a usage message; in CI this masks the real drift report because the report is printed before the crash only if drift exists — actually the crash happens at line 78 before any report is printed, so the guard produces zero output and an unhandled-exception exit.
- Fix: Parse args explicitly: `if "--fix" in argv: i = argv.index("--fix"); fix = argv[i+1] if i+1 < len(argv) else usage_error()`. Also reject unknown `--fix` values (anything not in `{A>B, B>A}` currently falls through silently and behaves like "no fix").

**[MEDIUM] Whitelist/ignore matching on basename allows unintended divergence escapes** - `lines 48-51`
- What: `_match` tests both the full relative path *and* `os.path.basename(rel)` against every pattern. So `build.py`, `verify.py`, `creator_cert.pem`, `AssetForge.spec`, etc. are whitelisted **anywhere in the tree**, not just at the root. A shared `forge/verify.py` or `tools/build.py` that drifts (or exists one-sided) is silently classified as intentional.
- Trigger: A new file added to both builds whose basename collides with a root-level whitelist entry, then edited on one side only.
- Impact: Real drift is reported as "intentional divergence" (or invisible for one-sided files) and the guard exits 0 — precisely the AF-2/3 class of bug this tool was built to catch.
- Fix: Drop the basename fallback for whitelist patterns (keep it only where genuinely intended, e.g. `*.md`), or anchor patterns explicitly (`"./build.py"`).

**[LOW] Directory pruning by bare name silently skips unintended subtrees** - `line 57`
- What: `dirs[:] = [d for d in dirs if d not in ("__pycache__", ".buildenv", "build", "dist")]` prunes *any* directory named `build` or `dist` at any depth — but `IGNORE` patterns like `"build/*"` only cover the root. A legitimate shared source dir named `src/build/` would never be compared on either side.
- Trigger: Someone adds a package directory named `build` or `dist` containing real code.
- Impact: Files vanish from both `_walk` maps silently — no drift, no one-sided warning, exit 0.
- Fix: Only prune when the relative path of the directory matches an IGNORE pattern via `_match`, instead of a hardcoded name set.

**[LOW] `--fix` path skips the token-drift guard and partially-fixes on error** - `lines 105-114, 121-127`
- What: When `--fix` succeeds, `main` returns 0 immediately, so `check_tokens` never runs. And if `shutil.copyfile` raises mid-loop (permissions, locked file on Windows), earlier files are already copied — the trees are left in a new, unreported mixed state.
- Trigger: `--fix` run, or a copy failure halfway through the drift list.
- Impact: Incomplete sync presented as success; token drift undetected on fix runs.
- Fix: Run `check_tokens` on all exit paths, and either pre-validate writability of all targets or copy to temp files and rename atomically per file.

## Missing safeguards
- No argument validation: unknown flags and invalid `--fix` values are silently ignored; add a usage error path (and tests for it).
- No test coverage for `_match` semantics (basename collision cases), the `--fix` direction mapping, or the `IndexError` path — these are exactly the defects above.
- `_sha` has no error handling for unreadable/vanishing files (TOCTOU between `_walk` and `_sha`); a single permission error kills the whole run with a traceback.
- No backup/dry-run mode for `--fix`; given it overwrites files in place, a `--dry-run` (print what would be copied) should be the default.
- One-sided files only WARN — consider a hard fail or an explicit allowlist-acknowledgement mechanism so warnings can't rot in CI logs.