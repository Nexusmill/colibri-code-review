# GATE_ADOPTION_PLAYBOOK.md - adopting the adversarial commit gate, end to end

> **The offering.** This is the complete, novice-grade runbook for the G39 adversarial
> commit-gate solution: every commit of code is independently reviewed by an external
> model before it can land, every landed commit carries durable cryptographic evidence
> of that review, un-evidenced history cannot be pushed, and the server re-verifies
> everything on every push. Written 2026-08-31, the day the full four-layer system went
> live across five repos (nexusmill, Tools, colibri-code-review, colibri-marketplace,
> caliper). Follow it top to bottom on a fresh repo and you end up with the same
> protection. Every step shows the exact command AND what you should see. If what you
> see differs, STOP and read the Troubleshooting chapter - do not improvise around the
> gate; improvising around the gate is the exact failure mode it exists to stop.

---

## Chapter 0 - What this is and why it exists

**The problem.** Authors defend invented claims. That includes AI agents reviewing
their own work: the gate was born the day a plan-triangulation exercise proved the
in-session agent (and two external models) each confidently defended wrong claims about
code none of them had actually read. Self-review is structurally untrustworthy.

**The solution, in one sentence:** no commit that stages code can land unless an
INDEPENDENT external model has read the exact staged bytes and issued `VERDICT: CLEAR`
- and every landed commit carries a durable, machine-verifiable record of that
clearance which travels with the history and is re-checked by CI.

**The four layers** (a pre-commit hook alone is advisory - git offers `--no-verify`,
plumbing, GUI escapes, unarmed clones, and, worst, direct forgery of the gate's own
state file):

| Layer | Mechanism | What it stops |
|---|---|---|
| 0 (the wall) | `pre-commit` hook -> `adversary_gate.py check` | ordinary ungated commits |
| 1 | the repo's commit driver calls `check`/`record` directly | commits from a disarmed clone via the driver |
| 2 | Claude Code PreToolUse deny-guard (`harness_guard.py`) | the agent-reachable bypasses AND the forgery route |
| 3 (the catch-all) | post-commit notarization into git notes + `pre-push` guard + vendored auditor | EVERYTHING, after the fact - it reads immutable output, not process |
| 4 | CI re-audit + branch protection (enforce_admins, linear history) | bypass reaching the shared remote |

**The honest contract (never oversell this):** a human at a shell can always bypass
client-side enforcement, and that is fine - the one-shot OVERRIDE escape belongs to the
owner anyway. Layers 1-2 bind agents operating through the harness; layer 3 detects
everything else; layer 4 makes bypass fail at the remote. Detection is the guarantee.
Prevention is not claimed.

**What counts as code** (the gated set): files with extensions `.py .js .json .ts .jsx
.tsx .html .css .ps1 .sh .bat .c .cpp .h .rs .go .java .glsl .osl`; ANYTHING under
`.githooks/` or `.github/workflows/` (enforcement config is gated config); deletions of
code files and renames-away; merges. `.json` is deliberately included (since
2026-08-31): manifests, registries and configs are load-bearing - a forged manifest row
is a code change. Plain `.md` documentation passes free.

---

## Chapter 1 - Prerequisites (check ALL of these before starting)

You need, on the machine that will commit:

1. **git** at `C:\Program Files\Git\cmd\git.exe` (or on PATH).
2. **Python 3.11+** at `C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe`
   (or on PATH as `python` - the shims try the exact path first, then PATH).
3. **The Tools repo at its canonical path**: `C:\Users\User\source\repos\Tools`.
   This is non-negotiable: every hook shim execs the gate from that exact path. On a
   machine WITHOUT it, arming a repo produces a deliberate LOCKOUT (every commit
   refused, none clearable) - that is fail-closed design, not a bug. Provision the
   machine first. Full machine-provisioning list: [EXTERNAL_SUBAGENT.md](EXTERNAL_SUBAGENT.md).
4. **An OpenRouter key** in the environment as `OPENROUTER_API_KEY`. The reviewer runs
   on OpenRouter. Cost is real but small (roughly a cent per commit with the
   recommended model).
5. **The gh CLI authenticated** (only needed for the CI/branch-protection chapters):
   `gh auth status` must show a logged-in keyring account, and the token must carry
   the **`workflow` scope** if you will ever push a repo containing
   `.github/workflows/` files - GitHub rejects such a push outright without it
   (`refusing to allow an OAuth App to create or update workflow ... without
   'workflow' scope` - hit live on this system's first push). Add it once with
   `gh auth refresh -h github.com -s workflow` (one browser device-code prompt).
   NOTE (documented owner fact, 2026-08-31): this machine's single gh keyring
   credential is valid for BOTH sites - the personal `github.com/phantom-man` account
   AND the `github.com/Nexusmill` org. You do not need a second login to work across
   them.

Verify the reviewer works before touching any repo:

```
python C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py --help
```

Expected: the argparse usage listing `check`, `run`, `record`, `check-push`, `status`.
If instead you get a traceback or "file not found", fix prerequisite 3 first.

---

## Chapter 2 - Arming a repo (the installer does everything; you prove it worked)

### Step 2.1 - run the installer

```
python C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py <path-to-repo>
```

Expected output: `ARMED  <repo-root>` followed by a summary line and a numbered
`NEXT` list. Exit code 0. What it just did (idempotent, re-run any time):

- copied the three canonical hook shims - `pre-commit` (the wall), `post-commit` (the
  notary), `pre-push` (the push guard) - into `<repo>/.githooks/`, LF-enforced,
  byte-verified;
- vendored the self-contained auditor `adversary_audit.py` beside them (so CI can run
  it with no external tooling);
- wrote `.githooks/adversary_baseline` = the current HEAD sha. This anchors the
  tripwire: commits BEFORE this moment were never notarized and can never be
  retroactively proven, so the auditor starts here. **The baseline is written once and
  never moved by a re-run** - if you think it is wrong, that is an installer bug, not
  a thing to hand-edit;
- pinned everything `eol=lf` in `.githooks/.gitattributes` (a CRLF-mangled shim is a
  script /bin/sh refuses to run);
- added `.adversary/` to the repo's `.gitignore` (transient gate state, never history);
- set `git config core.hooksPath .githooks` (THE arming - per clone, because git
  cannot ship config; **a fresh clone of an armed repo is UNARMED until this installer
  or that one config line runs in it**);
- set `git config notes.rewriteRef refs/notes/adversary` (so amend/rebase carry the
  evidence notes onto rewritten commits instead of orphaning them).

Exit code 3 instead of 0 means ARMED-BUT-FAIL-CLOSED: the Tools repo is missing at the
canonical path, so every commit will be refused and none can clear. Exit 1 = conflict
(foreign hooksPath or tampered shim - re-run with `--force` only after understanding
what you are overwriting).

### Step 2.2 - stage the arming files and record the executable bit

```
cd <repo>
git add .githooks .gitignore
git update-index --chmod=+x .githooks/pre-commit .githooks/post-commit .githooks/pre-push
```

The `--chmod=+x` line is REQUIRED and easy to forget. Windows cannot set a real exec
bit, and **POSIX git silently SKIPS a hook whose index mode is 100644** - which turns
the entire mandatory gate into a no-op on any Linux/macOS checkout. Three repos
shipped exactly that fail-open before it was caught. The index mode is what clones
inherit; record it.

### Step 2.3 - attempt the commit and WATCH IT GET REFUSED

```
git commit -m "chore(gate): arm the mandatory adversarial commit gate (G39)"
```

Expected: the commit FAILS with:

```
ADVERSARY GATE: commit REFUSED - staged code lacks a fresh adversarial clearance:
  .githooks/pre-commit    unreviewed
  ...
```

**That refusal is the end-to-end proof the hook fires in this clone.** If the commit
SUCCEEDS here, something is broken - stop and audit with
`install_gate.py <repo> --verify-only` (it prints per-component state: hooksPath, each
shim canonical/crlf/different/absent, auditor, baseline, rewriteRef).

### Step 2.4 - obtain the clearance and commit for real

```
python C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py run --model z-ai/glm-5.2 --context "arming commit: canonical shims + vendored auditor installed by install_gate.py"
git commit -m "chore(gate): arm the mandatory adversarial commit gate (G39)"
```

Expected from `run`: the reviewer's analysis, then `VERDICT: CLEAR`, then
`Clearance written for N file(s)`. Expected from the commit: it now succeeds, and the
post-commit hook prints `adversary record: CLEAR note written for <sha>`.

### Step 2.5 - verify the durable evidence exists

```
git notes --ref refs/notes/adversary show HEAD
python <repo>/.githooks/adversary_audit.py --repo <repo>
```

Expected: the first prints a JSON note (`"type": "CLEAR"`, per-file sha256s, the
embedded reviewer artifact). The second prints
`clean - every code commit carries a matching adversary note`. The repo is now armed
with all client-side layers. Do Chapter 4 (CI) before the first push.

---

## Chapter 3 - Daily work under the gate (the loop you will actually live in)

1. **Finish ALL edits first.** Clearances are keyed to the exact staged blob sha256s;
   any re-edit or re-staging of different bytes invalidates them by design. Review
   last, commit immediately after.
2. **Stage** everything that belongs in the commit (including the manifest `.json`
   rows describing the change - they are gated code and get reviewed WITH the change
   they describe, which is exactly right).
3. **Run the adversary:**
   ```
   python C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py run --model z-ai/glm-5.2
   ```
   Optionally add `--context "..."` with design intent the reviewer should know
   (deliberate trade-offs, provenance of copied bytes, links to prior clearances).
4. **On `VERDICT: BLOCK`:** read every finding. For each one either (a) FIX it, restage,
   and re-run, or (b) REBUT it factually via
   `run --context "finding X is wrong because <file:line evidence>"` - the reviewer
   re-verifies rebuttals against the bytes and will call out a false rebuttal (it has,
   twice, against the agent that built this system). Never argue in prose outside the
   loop, never shop for a compliant model, NEVER touch `.adversary/OVERRIDE` (the
   owner's one-shot escape; an agent using it is a protocol violation equal to
   disabling the gate).
5. **On `VERDICT: CLEAR`:** commit immediately, before anything re-edits the files.
   The post-commit hook notarizes automatically; you should see
   `adversary record: CLEAR note written`.
6. **Push normally.** The pre-push guard audits the outgoing commits (refusing the
   push if any code commit lacks its note) and then pushes `refs/notes/adversary` to
   the same remote automatically - the evidence always travels with the history; you
   never push notes by hand.

Model guidance (field-tested): `z-ai/glm-5.2` reviews in ~2 minutes with substantive
traces and is the recommended default flag. The built-in default `tencent/hy3` is
cheaper but has hung for 50 minutes and returned empty (the gate correctly fails
closed with BLOCK on an empty response - that is the designed behavior, not a crash).

Merging: merges are NOT exempt (a merge can carry un-gated commits). Do merges
LOCALLY, where the staged merge result goes through `run` like any change and gets
notarized like any commit. Never use the GitHub merge/squash/rebase buttons on a
gated repo - a server-side merge commit is created where no notary exists, can never
carry a note, and would turn the audit permanently red (Chapter 5 disables those
buttons for exactly this reason).

---

## Chapter 4 - CI: the server re-audits every push

Copy the workflow (byte-identical across all five adopted repos) to
`<repo>/.github/workflows/adversary-audit.yml`:

```yaml
name: adversary-audit
# push only, deliberately: a pull_request run checks out GitHub's SYNTHETIC merge commit
# (refs/pull/N/merge), which is created server-side and can never carry a note - the
# auditor would flag every PR as a violation. Push runs report the check on the real
# head sha, which is what required status checks match.
on:
  push:
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Fetch adversary notes
        run: git fetch origin +refs/notes/adversary:refs/notes/adversary || echo "no adversary notes ref on origin - unnotarized code commits will fail below"
      - name: Audit history against adversary notes
        run: python3 .githooks/adversary_audit.py --repo .
```

Note `.github/workflows/` is itself gated, so committing this file requires a
clearance (step 3 loop). That is intentional: enforcement config never changes
without an independent CLEAR. The vendored `.githooks/adversary_audit.py` is
self-contained stdlib Python and resolves git from PATH, so the ubuntu runner needs
nothing else. It recomputes every changed blob's sha256 per commit after the baseline
and demands a matching CLEAR note; owner OVERRIDE notes pass but are listed loudly.

---

## Chapter 5 - The owner's irreducible steps (one script, three parts)

Some steps can only be done by the OWNER (an agent attempting them is blocked by the
permission harness, correctly - they alter the harness itself, the credential's
scopes, and the shared remote's rules). All of them live in ONE idempotent script,
no elevation needed, one interactive moment (a browser device-code prompt in Part B):

```
python C:\Users\User\source\repos\Tools\adversary-gate\owner_setup.py
```

**Part A** registers the layer-2 harness deny-guard as a Claude Code PreToolUse hook
in `~/.claude/settings.json` (backup written first; restart Claude Code or open
`/hooks` once afterwards). Until this is live, an agent could forge
`.adversary/clearance.json` with correct sha256s and every other layer stays green -
this is the pivot of the whole design, not optional polish. The guard is GLOBAL to
the machine: every repo touched through Claude Code loses `git --no-verify`,
hooksPath re-pointing, `commit-tree`/`update-ref` plumbing, mutating `git notes`, and
all `.adversary/**` writes. It fails OPEN on malformed input (never bricks the
harness) - the wall and the tripwire stand behind it.

**Part B** adds the `workflow` scope to the gh token if missing (Chapter 1, prereq 5;
one device-code prompt) and then performs the outstanding pushes. Each push runs the
armed pre-push guard: outgoing history is audited and `refs/notes/adversary` is
pushed to the same remote automatically.

**Part C** sets branch protection on every adopted repo with a remote:
`enforce_admins: true` (the required `audit` check binds the owner's own pushes too),
`required_linear_history: true`, required check context `audit`, and PATCHes the repo
to reduce the UI merge strategies to squash-only. Two platform constraints, both found
live: GitHub refuses disabling all three strategies (422 `no_merge_method`), AND under
linear-history protection it refuses merge-commit-only — the truly inert choice, since
that button can never succeed under linear history — demanding squash or rebase (422
`protected_branch_policy`). Squash-only is the platform floor: the one remaining button
mints a single unaudited sha per misuse (rebase would mint N), and any use turns the
audit red on the protected branch. For the UI-merge path this is detection, not
prevention — the platform will not allow better; do not use the button. Consequence, stated plainly: a
protected branch only ever moves by fast-forwarding a sha that ALREADY passed the
audit check on another branch. Push your work to a feature branch, let CI go green,
then fast-forward the protected branch to that same sha. If Part C fails with a
check-context error, the repo simply has no CI run yet - the pushed workflows must
finish once; then re-run the script (Parts A and B become no-ops).

---

## Chapter 6 - Verification checklist (run after adopting; all must pass)

| # | Command | Must show |
|---|---|---|
| 1 | `install_gate.py <repo> --verify-only` | `ARMED`, every component `canonical`/`present`, exit 0 |
| 2 | `git config core.hooksPath` | `.githooks` |
| 3 | `git ls-files -s .githooks/pre-commit .githooks/post-commit .githooks/pre-push` | mode `100755` on all three |
| 4 | stage a junk `.py`, `git commit` | `ADVERSARY GATE: commit REFUSED` (then `git reset`) |
| 5 | `.githooks/adversary_audit.py --repo <repo>` | `clean - every code commit carries a matching adversary note` |
| 6 | `git push` of a branch | notes ref appears on the remote (`git ls-remote <remote> refs/notes/adversary`) |
| 7 | GitHub Actions after push | the `audit` job green |
| 8 | (after owner_setup) agent runs `git commit --no-verify` | denied with a G39 message |

---

## Chapter 7 - Troubleshooting (every entry below actually happened)

- **The reviewer hangs for tens of minutes / returns empty.** `tencent/hy3` burned 50
  minutes of reasoning and returned no content; the gate printed
  `(model returned no content - failing closed)` and BLOCKed. That is correct
  behavior. Re-run with `--model z-ai/glm-5.2`.
- **Commit succeeded when it should have been refused.** Almost always the 100644
  exec-mode fail-open (POSIX skips non-executable hooks) or an unarmed clone
  (`core.hooksPath` unset). Run `--verify-only`; re-run the installer; redo step 2.2.
- **`/bin/sh: ... pre-commit: not found` or hook syntax errors.** CRLF-corrupted shim
  (an `autocrlf=true` checkout rewrote it). `--verify-only` reports `crlf`; a plain
  installer re-run repairs it; the `.gitattributes` pin prevents recurrence.
- **CI red on every PR.** You added `pull_request` to the workflow triggers. GitHub's
  synthetic PR merge commit can never carry a note. Push-only triggers (Chapter 4).
- **CI red: `UNNOTARIZED` on commits you know were reviewed.** The notes ref did not
  reach the remote. The pre-push guard normally pushes it automatically; if the push
  happened from a clone without the guard, push notes by hand once:
  `git push <remote> refs/notes/adversary`.
- **Pre-push refuses: "notes push FAILED".** Notes diverged (another clone pushed
  notes). Recover exactly as the message says:
  `git fetch <remote> +refs/notes/adversary:refs/notes/adversary-theirs` then
  `git notes --ref refs/notes/adversary merge -s cat_sort_uniq refs/notes/adversary-theirs`,
  then push again.
- **Pre-push refuses on OLD commits that predate the gate.** Two known causes. (a)
  Your gate version predates the single-`--not` fix: `rev-list --not A --not B`
  TOGGLES, so the guard's original two-`--not` range re-INCLUDED the whole
  pre-baseline history and refused fully notarized pushes - caught on this system's
  FIRST live push, fixed same hour (Tools 4cfbf34, regression-tested); update the
  Tools repo. (b) The baseline file is wrong or missing - re-run the installer (never
  hand-edit the baseline to make a refusal go away).
- **Push rejected: `refusing to allow an OAuth App to create or update workflow ...
  without 'workflow' scope`.** GitHub, not the gate: the gh token cannot push
  `.github/workflows/` files. `gh auth refresh -h github.com -s workflow` once
  (Chapter 1 prereq 5), then push again. Note the pre-push guard had already audited
  the range and pushed the notes ref before GitHub rejected the branch - a rejected
  branch push with notes on the remote is a harmless intermediate state.
- **Rebase/amend "lost" the clearance notes.** `notes.rewriteRef` was unset (old
  arming). Installer re-run sets it. Notes for unchanged blobs survive a rebase;
  changed blobs correctly need fresh review.
- **A `--verify-only` says UNARMED after an npm install.** Husky-style hook managers
  re-point `core.hooksPath` silently. The installer warns about this at arming time;
  re-run it to re-arm, and re-verify after every npm install in such repos.
- **An agent claims a step is "blocked by permissions".** Steps that edit
  `~/.claude/settings.json` or GitHub repo settings are OWNER steps by design -
  that is Chapter 5's script, not something to work around.
- **Two GitHub sites, one credential.** This machine pushes to both
  `github.com/phantom-man` and `github.com/Nexusmill` with the single gh keyring
  login. If auth fails on one of them, fix the keyring login once - do not create
  per-site tokens.

---

## Chapter 8 - What the evidence looks like (so you can audit by hand)

A notarized commit carries a JSON note on `refs/notes/adversary`:

```
git notes --ref refs/notes/adversary show <sha>
```

```json
{
 "type": "CLEAR",
 "commit": "<full sha>",
 "when": "20260831-024812",
 "files": {"path/file.py": {"sha": "<sha256 of the committed blob>",
            "model": "z-ai/glm-5.2", "when": "...", "artifact": ".adversary/reviews/gate_....md"}},
 "artifacts": {".adversary/reviews/gate_....md": "<the reviewer's full verdict text>"}
}
```

The auditor recomputes each changed blob's sha256 from the commit itself and compares.
Residual risk, stated honestly: a determined fraudster could forge a note with correct
shas and fabricated verdict text; the embedded artifact makes that CHECKABLE (re-run a
review against the same bytes and compare), and the layer-2 guard denies agents the
write paths. Detection, not prevention, by design.

## Related docs

[LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md) (the threat model in depth) ·
[ADVERSARY_GATE.md](ADVERSARY_GATE.md) (the wall itself) ·
[GATE_INSTALLER.md](GATE_INSTALLER.md) (installer reference) ·
[EXTERNAL_SUBAGENT.md](EXTERNAL_SUBAGENT.md) (provisioning a second machine)
