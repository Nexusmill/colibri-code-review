# Colibri bug review — tools/git-guard.mjs

reviewer: zcode-subagent-fresh-context (GLM-5.3) · mode: bug · date: 2026-09-03
sha256: 1c33320bdf2e98a5f3408acd9616f2bd1d6d33d61f103c67e31a5909159882af

### Meta
- path: tools/git-guard.mjs | sha8: 1c33320b | lines: 63 | context-pack: installed cache copy at C:/Users/User/.zcode/cli/plugins/cache/tools/universal-tools/1.0.0/hooks/git-guard.mjs is byte-identical (sha8 1c33320b — no drift); deny protocol matches the working sibling protocol-gate.mjs (stdout JSON `permissionDecision` + exit 0); deny classes live-tested in a temp repo with a marker pre-commit hook; regex battery 37/37 against faithful transcription of lines 37-57.

### Review

## Verdict
Ships the intended four deny classes for their literal spellings, but as a security control it is porous: four distinct working bypasses were confirmed by live execution (separate-token `-n`, env-var `core.hooksPath` injection, backslash-escaped `comm\it`, interpreter/verb-gap writes into `.git/hooks`), plus a false positive on `-mn`. The inner git hook remains the real gate; this layer needs token-based matching, not substring adjacency.

## Bugs & vulnerabilities
**[HIGH] Separate-token `-n` bypasses the --no-verify deny** - `line 37` — CONFIRMED
- What: the short-bundle regex `\bcommit\s+-[a-z]*n[a-z]*` only matches `n` glued to the FIRST option cluster directly after `commit`. `git commit -q -n -m x`, `git commit -m x -n`, `git commit --amend -n` all pass (battery: ALLOW; live run of `git commit -q -n --allow-empty -m t3` in a temp repo: exit 0, pre-commit hook did NOT run, commit created).
- Trigger: any commit with `-n` as its own token after another flag.
- Impact: working bypass of the protected review gate with a completely natural-looking command — no obfuscation needed.
- Fix: once the `git ... commit` invocation matches, deny on any whitespace-separated token equal to `-n` or `--no-verify` (i.e. decouple the flag scan from adjacency), keeping the bundle regex for glued forms.

**[HIGH] Env-var config injection redirects core.hooksPath unseen** - `lines 45-47` — CONFIRMED
- What: rule 3 requires the literal word `git` BEFORE `core.hooksPath` (`\bgit\b[^|;&]*core\.hooksPath`). Git's documented `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0=core.hooksPath`/`GIT_CONFIG_VALUE_0=...` env mechanism puts the string BEFORE `git`, so `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/tmp/emptyhooks git commit -m x` passes every rule. Live run: exit 0, hook did NOT run.
- Trigger: one-line env-prefixed commit.
- Impact: full hooksPath redirection — the exact evasion class the header names — with zero obfuscation.
- Fix: scan the whole command for `core\.hooksPath` (or `GIT_CONFIG_KEY_\d+`) whenever any git invocation is present, regardless of position relative to `git`.

**[HIGH] Shell lexical evasion (`comm\it`, variable indirection) hides the commit word** - `line 37` — CONFIRMED
- What: `git comm\it --no-verify` (bash unescapes to `git commit`) fails `\bcommit\b`, so `--no-verify` is never even checked; same for `c=git; $c commit --no-verify`. Live run of the escaped form: exit 0, commit created, hook did NOT run; both pass the guard (battery: ALLOW).
- Trigger: backslash/quote-split or variable-built command words.
- Impact: trivially working bypass; the flag itself is visible in the string but only checked conditionally on the `git commit` adjacency.
- Fix: decouple the flag checks from the invocation match — deny `--no-verify`/`-n` tokens whenever the command contains any git-ish token (`\bgit\b`, `git.exe`, `$GIT*`), not only after a matched `commit`. Full variable/eval indirection of the flag itself stays beyond regex reach; document that residual.

**[HIGH] Rule 4's verb allowlist leaves .git/hooks writes wide open** - `line 49` — CONFIRMED
- What: Bash-side protection requires `\b(rm|mv|cp|tee|chmod|truncate)\b` or a `>` redirect adjacent to a `.git/hooks` path. `sed -i s/x/y/ .git/hooks/pre-commit`, `node -e "require('fs').writeFileSync('.git/hooks/pre-commit','x')"`, `powershell Set-Content ...`, `cmd /c del E:\...\.git\hooks\pre-commit`, `dd of=`, `git apply` all pass (battery: ALLOW). This is not hypothetical: this review itself installed a pre-commit hook via `node -e fs.writeFileSync` through the live armed guard without a denial.
- Trigger: any write/delete into `.git/hooks` via a verb outside the six listed.
- Impact: "deleting the hook file" — an evasion class the header explicitly claims to close — works via a one-liner.
- Fix: invert the logic — when a `.git[\\/]hooks` path appears (case-insensitive, see next finding), deny unless the command is a recognizable read-only verb (ls/cat/git status/log/rev-parse...); or extend the verb set (sed, awk, perl, python, node, dd, install, rsync, del, rd, move, ren, git apply, patch) and flag `-e`/`-i` script flags. Consider denying ANY non-read command mentioning `.git/hooks`.

**[MEDIUM] Case-sensitive path regexes vs case-insensitive NTFS** - `lines 49, 57` — CONFIRMED (Bash) / PLAUSIBLE (Edit path)
- What: `\.git[\\/]hooks` and `[\\/]\.git[\\/]hooks[\\/]` are case-sensitive. `rm E:/AI/Caliper/.GIT/HOOKS/pre-commit` passes rule 4 (battery: ALLOW) and deletes the real file on Windows; `E:/AI/Caliper/.GIT/Hooks/pre-commit` passes the Edit/Write check (battery: ALLOW) — PLAUSIBLE there only because the harness may canonicalize case before the hook sees it.
- Trigger: mixed-case `.git/hooks` path.
- Impact: both file-tool and Bash protection bypassable by case games on Windows.
- Fix: add the `i` flag to both path regexes (and normalize separators).

**[MEDIUM] False positive: `git commit -mn` is denied although the hook runs** - `line 37` — CONFIRMED
- What: git parses `-mn` as `-m "n"` (glued value), not `-m -n`. Live run: exit 0, pre-commit hook RAN, commit subject literally `n` — the review gate was intact — yet `-[a-z]*n[a-z]*` matches `mn` and denies. Same class: any bundle where `n` glues to a value-taking short option.
- Trigger: `git commit -mn ...`.
- Impact: legitimate (hook-running) commits blocked; availability defect in a deny-control, and it advertises the adjacency weakness.
- Fix: only treat `n` as the flag when it is a standalone token or the bundle contains no value-taking short option before it; tokenizing per the first fix largely subsumes this.

**[LOW] Read/command false positives beyond the accepted hooksPath-read quirk** - `lines 37-49` — CONFIRMED
- What: the known accepted quirk (read `git config core.hooksPath` denied) is NOT the only one — battery confirms: `git grep core.hooksPath` (R3), `git log --grep=update-ref` (R2), `echo "... git commit --no-verify is banned"` (R1, since `--no-verify` is checked command-wide once `git ... commit` matches anywhere), and `ls .git/hooks && rm -rf node_modules` (R4, unrelated `rm` satisfies the verb test when both substrings exist) are all denied though none touches the gate.
- Trigger: any command merely quoting/searching for the guarded strings.
- Impact: read-only and documentation commands blocked (deny-direction, no security loss).
- Fix: for R1, check `--no-verify`/`-n` only within the same shell segment as the commit; for R4, require the verb and the `.git/hooks` path in the same segment/argument context.

**[LOW] Denial JSON can in principle be dropped by immediate process.exit on a Windows pipe** - `lines 24-25` — PLAUSIBLE
- What: `process.stdout.write(...)` to a pipe is asynchronous on Windows; `process.exit(0)` immediately after can abandon the queued write (long-documented Node footgun). Experiment here (400 piped child runs of the exact deny payload): 0 drops — not reproduced in this environment, and the sibling protocol-gate.mjs (lines 42-44) shares the pattern and demonstrably works in production, so this is intermittent/theoretical only — unverified because it needs a losing race under load.
- Trigger: OS-level timing between the pipe write completing and process teardown.
- Impact: a denial silently becomes an allow (exit 0, empty stdout).
- Fix: `process.stdout.write(data, () => process.exit(0))`, or set `process.exitCode = 0` and let the loop drain.

## Missing safeguards
- The guard's own installation is unprotected: `rm C:/Users/User/.zcode/.../hooks/git-guard.mjs` and editing that `hooks/hooks.json` (Edit file_path check only looks for `.git/hooks`) both pass — battery: ALLOW. An adversarial agent can uninstall the outer layer first; only the inner git hook remains.
- Whole-`.git` removal (`rm -rf E:/AI/Caliper/.git`) passes all rules — destroys the gate (and the repo); the hooks-subdir patterns are narrower than the asset they protect.
- Tool coverage is exactly `Bash|Edit|Write|MultiEdit`: MCP write tools (this harness's `universal-tools safe_write`/`safe_replace`, `node_repl js`) can write `.git/hooks/pre-commit` without any PreToolUse matcher firing.
- No env-var scanning at all: beyond `core.hooksPath`, `GIT_CONFIG_KEY_*` can also set e.g. `commit.gpgsign=false` or alias-style config — nothing checks env assignments.
- Relative-path gap: `.git/hooks/pre-commit` (no leading separator) misses the file-path regex — mitigated today only because the harness requires absolute file paths in Edit/Write; the guard itself does not enforce it.
- Deny log grows unbounded (`~/.zcode/git-guard.log`), no rotation; fine for now, worth noting.
- Fail-open boundary (line 29) is deliberate and correct for parse errors; note it also swallows a valid-JSON-but-wrong-shape payload (e.g., `tool_input` a string) into a silent allow — acceptable per doctrine, but a one-line shape assert would tighten it without bricking risk.
