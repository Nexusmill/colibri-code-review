# Colibri review — adversary-gate/harness_guard.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\adversary-gate\harness_guard.py`
- **Model:** claude-fable-5 (in-session)
- **sha256:** `379b2cdf45221adb11af14732871dca64d467657075b3262b740f04d2e26744a`
- **Date:** 2026-09-02
- **Mode:** bug
- **Context pack:** jCodemunch outline + repo-wide `harness_guard` references (guard_selftest.py drives the real hook; owner_setup.py PART A registers it machine-wide as a PreToolUse hook on Bash|Write|Edit|NotebookEdit); TOOLS_MANIFEST covenant; G39 layered-enforcement doctrine (this file is layer 2; the forgery route — writing `.adversary/clearance.json` — is the one bypass that defeats ALL layers, because a forged CLEAR with correct staged blob shas passes the hook and gets notarized as a valid note, so the L3 audit reads green). Deliberate designs honored: fail-OPEN on malformed stdin, prose over-blocking accepted, human-at-shell bypass out of scope.
- **Verification:** every finding below was driven through the real `decide()` via an importlib probe (scratchpad `hg_probe.py`); the Windows canonicalization claim was proven with a live filesystem write. No finding is by-inspection-only.

## Verdict
Not shippable as the forgery-route lock it claims to be: the two exemption regexes and Windows path canonicalization each reopen agent-reachable writes to the gate's own state. The regex rules that have no exemption clause (plain `--no-verify`, notes mutation, plumbing) hold.

## Bugs & vulnerabilities

**[HIGH] Exemption is a whole-command substring — a comment naming the gate tooling unlocks `.adversary` writes** — `line 55-58`, `decide()` line 77-83
- What: rule 8 blocks any Bash command mentioning `.adversary`, EXCEPT when the command also matches `(adversary_gate\.py|adversary_audit\.py|install_gate\.py|guard_selftest\.py)` — anywhere in the command text.
- Trigger: `echo CLEAR > .adversary/clearance.json  # adversary_gate.py` → **allowed** (probe A2).
- Impact: the forgery route this guard exists to close (G39 layer 2's stated purpose) is reopened by a trailing comment. A forged clearance keyed to the staged blob shas passes the pre-commit hook and is then notarized by `record`, so even the L3 audit reads green — this is the one bypass with no backstop.
- Fix: exemption must match the command *shape*, not a substring — e.g. exempt only when the command's first non-env token invokes python on one of the gate scripts (anchor the regex to the start: `^\s*(\S*python[\d.]*(\.exe)?\s+)?\S*(adversary_gate|adversary_audit|install_gate|guard_selftest)\.py\b`), and strip nothing else.

**[HIGH] Windows trailing-dot segment defeats the file-tool `.adversary` check** — `line 67-73`
- What: `decide()` splits the normalized path and requires a segment to equal `.adversary` exactly. Windows canonicalizes `.adversary.` (trailing dot, likewise trailing spaces) to `.adversary` at the filesystem layer.
- Trigger: Write/Edit with `file_path="repo\.adversary.\clearance.json"` → allowed (probe F2), and a live write through a trailing-dot directory segment lands in the real directory (probe C1: `landed-in-real-dir=True`).
- Impact: same forgery route as above, via the file tools this rule was added to close.
- Fix: strip trailing dots/spaces from each segment before comparison (`part.rstrip('. ')`); consider also matching the 8.3 short-name prefix (`advers~`) defensively.

**[MEDIUM-HIGH] hooksPath exemption matches a prefix, not the exact arming value** — `line 40-42`
- What: the negative lookahead exempts anything whose next token *starts with* `.githooks` up to a word boundary; `-`, `/`, `.` are word boundaries.
- Trigger: `git config core.hooksPath .githooks-evil` and `git config core.hooksPath ".githooks/../evil"` → both **allowed** (probes B2, B3); both re-point hooks to an attacker-chosen directory while looking armed.
- Impact: layer-0 disarm from the harness. Backstop exists (L3 audit flags the resulting unnotarized commits), so this is not forgery-class, but the rule's entire purpose is defeated.
- Fix: exempt only the exact token — require `\.githooks` followed by end-of-token: `hookspath(?![\s="']*\.githooks(?=[\s"';&|]|$))`.

**[LOW-MEDIUM] `--no-verify` smuggled across lines via a shell variable** — `line 34-36`
- What: rule 1 requires `git` and `--no-verify` on the same line (`[^\n]*`).
- Trigger: `FLAG=--no-verify` newline `git commit $FLAG -m x` → allowed (probe D2).
- Impact: bypasses layer 2 only; the unnotarized commit is caught by the L3 audit, and the guard's docstring already concedes regex-level honesty limits. Reported because the fix is one character class.
- Fix: also scan for a bare `--no-verify\b` token anywhere in a command that mentions `git` anywhere (drop the same-line coupling), accepting the wider false-positive surface the file already embraces.

## Missing safeguards
- **`git fast-import` and `git replace` are unlisted** (probes E2, E3 allowed). `fast-import` is `commit-tree`-class plumbing (creates commits with no hooks); `git replace` can substitute objects under the auditor unless it runs with `GIT_NO_REPLACE_OBJECTS` — flagged PLAUSIBLE pending the adversary_audit.py unit; if the auditor is replace-blind, `replace` is forgery-adjacent.
- **File tools may edit `.githooks/*` freely** (probe F3): live-noop the pre-commit hook via Edit, then plain `git commit` lands ungated (L1 only binds `_git_do.py` users). Caught by L3 at audit time, but layer 2 claims to cover "the classic hook bypasses". Tension: gate development legitimately edits `.githooks` — a rule here needs an exemption for the Tools repo or the installer flow, so this is a design decision for the owner, not a drop-in fix.
- No selftest case covers any of the four confirmed bypasses; `guard_selftest.py` should gain one row per fix (RED first).
