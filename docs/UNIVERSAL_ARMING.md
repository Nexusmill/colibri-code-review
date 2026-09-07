# UNIVERSAL_ARMING.md - machine-wide arming of the adversarial commit gate

> **Doc version: 1.1 - 2026-09-07.** New at 1.0; 1.1 adds the EV-043 post-rollout hardening
> section (the dispatcher self-check vs partial commits). Registered in [DOCS_VERSIONS.md](DOCS_VERSIONS.md).
> Source of truth: `Tools/adversary-gate/` (`hooks/` dispatchers, `install_gate.py`,
> `adversary_gate.py`, `adversary_audit.py`, `harness_guard.py`). Companions:
> [LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md) (the four layers),
> [ADVERSARY_GATE.md](ADVERSARY_GATE.md) (the wall), [GATE_INSTALLER.md](GATE_INSTALLER.md)
> (installer reference), [HARNESS_GUARD.md](HARNESS_GUARD.md) (layer 2),
> [CODEX_GATE_IMPLEMENTATION.md](CODEX_GATE_IMPLEMENTATION.md) (Codex-side), docket rows
> EV-041 and EV-042 in `gate_evidence.json`.

## Why this exists (EV-041)

Until 2026-09-06 the gate was armed **per clone**: `git config core.hooksPath .githooks`
run once in each working copy. `LAYERED_ENFORCEMENT.md` recorded "unarmed fresh clones
still commit un-gated" as an accepted residual, on the premise that *per-clone arming is a
git limitation*. While setting up Codex as a second harness, the owner called this a hole.

**The premise was false, and probing it turned up something live and worse.** Under a real
git process with a throwaway global config:

- A machine-global `core.hooksPath` arms a fresh `git init`, a fresh clone, and a fresh
  `git worktree add` with **no per-clone action at all**; a local `.githooks` value still
  wins where set. So a global hook path is not just possible, it is the natural fix.
- **Worse and live:** a worktree of an *already armed* repo, checked out on a branch that
  predates the vendored `.githooks/` directory, was committing **un-gated**. The inherited
  relative value `.githooks` did not resolve in that worktree, git ran no hook, and the
  commit succeeded. Two such worktrees existed on the owner's machine.

The fix is machine-wide arming, described below. The false-premise residual is retracted in
`LAYERED_ENFORCEMENT.md` (residual 4) and every doc that repeated it, and docketed as
EV-041. A second gap surfaced in the same work (EV-042): the canonical hook shims are
extensionless files that the code-class check never gated - see **HOOK_NAMES** below.

## The architecture, in one picture

```
git's GLOBAL core.hooksPath  ->  Tools/adversary-gate/hooks/   (owner sets this ONCE)
                                    pre-commit  post-commit  pre-push   (dispatcher shims)
                                        |  self-check, then gate check/record/check-push,
                                        |  then the repo's OWN default-dir hook if present
install_gate.py <repo>  ->  pins the SAME absolute dir as the repo's LOCAL core.hooksPath
                            + vendors .githooks/{shims,adversary_audit.py,baseline,epoch}
install_gate.py --census -> proves every checkout + worktree on the machine
```

Two independent settings both point at the same directory:

- **The global value** (owner-set, once, at a shell): arms every checkout and every future
  clone/worktree on the machine, including repos never touched by the installer.
- **The local pin** (installer-set, per repo): an **absolute** path, so a worktree inherits
  a value that resolves on any branch, and the repo stays armed even if the global value is
  later cleared. This replaces the old relative `.githooks`, which dangled in worktrees.

The vendored `.githooks/` directory stays in every armed repo. It is what CI runs (it has
no access to the owner's machine) and what other machines arm against with the classic
per-clone recipe. On the owner's machine it is redundant with the global dispatcher for the
commit wall, but it still carries the per-repo baseline, the rules epoch, and the auditor
that CI needs.

## The dispatcher shims (`Tools/adversary-gate/hooks/`)

Each shim, in order:

1. **Self-check.** The dispatchers execute from the suite's own working tree, so an
   uncommitted edit to a dispatcher would silently disarm every repo pinned to it. Each shim
   refuses to run while its own file is untracked in the suite checkout or differs from its
   committed HEAD blob (`pre-commit`/`pre-push` fail closed; `post-commit` warns and skips
   notarization). The one exception is the suite repo itself committing the dispatcher with
   the edit fully staged - that commit is gated, and the gate reviews the dispatcher as code
   (HOOK_NAMES). A tamper that also removes the self-check is not stopped at run time (no
   script defends against its own edit) - detection is the census and the audit tripwire.
2. **The gate.** `adversary_gate.py check` (pre-commit), `record` (post-commit), or
   `check-push "$remote"` (pre-push). `GATE=` is resolved from the shim's own location
   (`$0/..`), so a relocated copy of the suite execs *its own* gate rather than the
   authoring machine's path.
3. **The repo's own hook.** If the repo's default hook dir (`$(git rev-parse
   --git-common-dir)/hooks/<name>`) holds an executable hook of the same name, the shim
   execs it with the same arguments and stdin. This is why a repo with a pre-existing
   `pre-commit` (e.g. Nexusmill's `tools/git_guard.py`) keeps working - the adversary gate
   runs first, then the repo's own guard. The shim never chains into `.githooks/` (that shim
   execs the same gate - a double review).

## The census (`install_gate.py --census [ROOT ...]`)

Walks every checkout and worktree under the roots (default: the owner's repo roots,
`$CODEX_HOME/worktrees`, and the Codex documents dir), and every worktree each of them
lists. One row per checkout; exit 0 only when all are `armed`; exit 2 when no checkouts are
found (inspecting nothing is not success). `--verify-only` reports the same judgement for
one repo. Both share a single `_assess()` so they can never disagree.

| State | Meaning |
|---|---|
| `armed` | the effective hooks value resolves here AND the vendored `.githooks/` bytes are canonical (or absent on a pre-vendoring branch, under the absolute dir) AND the baseline and `notes.rewriteRef` are set |
| `stale` | the commit gate is live (the value resolves) but the vendored auditor / baseline / rewriteRef are not canonical - re-run the installer and commit `.githooks/`. **A never-installed foreign repo under the global value reads `stale`: it is commit-gated, but has no push guard, notary, or CI tripwire.** |
| `dangling` | the value resolves to NOTHING here - git runs no hook. A relative `.githooks` in a worktree whose branch lacks it, or an absolute dispatcher dir that is missing or lacks its three shims. Fail-closed reporting: exit non-zero |
| `tampered` | the effective value is the canonical dispatcher dir, but a dispatcher in it differs from its committed blob (or the suite is not a git checkout) - every pinned repo fails closed until it is committed through the gate |
| `unset` | no local and no global value |
| `overridden` | another hook system's value (a real, existing dir that is not ours) |

## HOOK_NAMES: hook files are code wherever they live (EV-042)

The code-class check gated `.githooks/` and known extensions. The canonical shims
(`Tools/adversary-gate/pre-commit`, `post-commit`, `pre-push` - the single source of every
vendored shim, and now the dispatchers under `hooks/`) are **extensionless files outside
`.githooks/`**, so they had never been gated code. Found from the gate's own status line in
round 1 of the arming work.

`HOOK_NAMES = ("pre-commit", "post-commit", "pre-push")` in both `adversary_gate.py` and the
vendored `adversary_audit.py` (a parity selftest keeps the two identical): an extensionless
file with one of these basenames is code wherever it lives. A commit that changes such a
file now needs a clearance and a note.

### The rules epoch (why HOOK_NAMES did not turn history into violations)

Reclassifying hook files as code would retroactively flag every historical commit that
touched a canonical shim while it was still docs-class - permanent, un-clearable violations
that would fail CI. The fix is a **per-repo rules epoch**:

- `install_gate.py` writes `.githooks/adversary_rules_epoch` once, containing
  `hook-names <sha>` where `<sha>` is HEAD at the moment a HOOK_NAMES-aware auditor is
  vendored. The HOOK_NAMES rule is confined to commits **strictly after** that sha; earlier
  hook-file commits keep the old (docs-class) classification.
- The epoch is read from **HEAD's tree only** (`git show HEAD:.githooks/adversary_rules_epoch`),
  never the working tree - a working-tree read is case-folded on Windows/macOS and follows
  symlinks, while the anchor is exact.
- The epoch is **anchored in history**: the recorded sha must be an ancestor of **every**
  commit that ever added the epoch file (order-independent, `--full-history`), so a later
  commit cannot rewrite it to a descendant and grandfather earlier hook-file commits out of
  the rule - not by a plain rewrite, not by a forged-date re-add on a merged side branch.
- Failure states all fail **closed** (the rule applies to every commit): `moved` (recorded
  sha is not an ancestor of every add), `uncommitted` (not yet in HEAD's tree), `unreadable`
  (shallow clone, or the history read failed).
- A legitimate squash/cherry-pick vendoring flow can leave the epoch `moved`; the owner
  recovers with `install_gate.py <repo> --reanchor-epoch`, which rewrites it to the common
  ancestor of the parents of every add (sound by construction, never a forward move) and
  refuses to touch a sound epoch.

## The hardening record (~17 blocked gate rounds)

The whole tranche was written test-first and every commit went through the gate itself.
Because the change touches the enforcement layer, the gate blocked it repeatedly - each
block a real defect of the author's, each fixed RED-first with the reviewer's own trigger
as a selftest row. A representative list, all on the author's own code:

- the staged tree could not pass its own selftest (the installer change was unstaged);
- HOOK_NAMES reclassified history -> the rules epoch;
- an absolute pin to a *missing* dispatcher dir printed `ARMED` -> dispatchers required
  before any pin, absolute-missing counts as dangling;
- partial dispatcher loss (pre-commit kept, pre-push gone) read `armed` -> all three
  required;
- dispatcher **content** was never verified, so a working-tree edit disarmed every repo ->
  the dispatcher self-check and a `tampered` state;
- the selftests' own fixture commits were unisolated from a global pin -> temp-global
  isolation;
- the guard side (see [HARNESS_GUARD.md](HARNESS_GUARD.md)): tab/NBSP and quote-adjacent and
  quote-glued suffixes on the arming value; the dispatcher dir agent-writable; a 256 KiB
  stdin cap that fell open on padded Codex payloads; a missing `multiedit` alias; trailing-dot
  and `z/..` and 8.3-alias spellings; a substitution and then a plain redirection riding
  inside the arming exemption; literal-free `--global`/`--system`/section/include config
  writes and the `GIT_CONFIG_*` env vars; quote-pair token splitting; a quadratic scan;
- the epoch anchoring: grandfather-by-later-commit, forged-date merge, shallow clone,
  case-variant path, symlink, and a missing replace-ref guard on the installer's own reads.

Final selftest counts on the landed bytes: guard 231, install 72, gate 65, hooks 10 (new),
audit 35, codex 19, arm_repo 17.

## Operating notes

- **The global value is the owner's, always.** The harness guard denies every agent write
  of a global/system hooks value (and every literal-free config write that could re-point
  it - see HARNESS_GUARD.md). Set it once at a shell:
  `git config --global core.hooksPath C:/Users/User/source/repos/Tools/adversary-gate/hooks`.
- **Prove the machine** with `install_gate.py --census`. On the owner's machine after the
  global command: the armed product repos read `armed`; never-installed foreign/scratch
  clones read `stale` (commit-gated, deliberately not fully installed); transient agent
  worktrees come and go.
- **Never index a delta-mode or specially-branched repo from the wrong branch expecting the
  hooks to follow** - that is a jCodemunch concern, unrelated; here the rule is simpler:
  the dispatcher runs on every commit regardless of branch.
- **When a change alters the vendored auditor**, re-vendor *all* armed repos
  (`install_gate.py <repo>` each) and commit the refreshed `.githooks/` through the gate. A
  clearance obtained against a superseded auditor is abandoned, not reused.

## Post-rollout hardening: EV-043 (the dispatcher self-check and partial commits, 2026-09-07)

The rollout's ~17 rounds were all *plain* commits (`git commit`), so they never exercised a
*partial* commit (`git commit -- <paths>`). The first partial commit after the machine-wide pin -
landing these very gate docs under the stage-explicit-paths discipline - exposed a defect in the
dispatcher self-check that the rollout could not have seen:

- **The false positive.** A partial commit makes git build a temporary index and export an
  ABSOLUTE `GIT_INDEX_FILE` to the hook. The self-check's `git -C "$SUITE"` commands inherited it
  and read the *committing* repo's temp index instead of the suite's, so `ls-files
  --error-unmatch hooks/pre-commit` failed and the check refused a byte-clean dispatcher with
  `dispatcher hooks/pre-commit is MODIFIED ... failing CLOSED`. Every partial commit from any
  armed non-suite repo was blocked with a misleading message. A plain commit leaks only a relative
  `.git/index`, which is why the rollout never hit it.
- **The dead-then-leaky exception.** The "suite may commit SELF fully staged" clause compared the
  committing repo's toplevel to the adversary-gate *subdir*, never equal - dead code since gate
  round 5. Reviving it (round 1) let an untracked dispatcher pass; narrowing it (round 2) still let
  a staged edit ride a partial commit of *other* paths while the modified dispatcher executed and
  was notarized clean.

**Fix (Tools `7ba0e3b`, three gate review rounds, each catching a real hole in the author's own
repair):** a `suite_git()` helper runs every suite-side git in a subshell with all repo-retargeting
`GIT_*` variables unset (index, dir, work-tree, common-dir, object dirs, namespace, the two config
channels, and the ceiling-directories variable), so `git -C "$SUITE"` always resolves the suite;
the gate invocation keeps the inherited index so a partial commit is still reviewed against the
partial set. The in-band exception is **removed entirely** - the self-check is now strictly
fail-closed, and a dispatcher edit is committed through the repo's `.githooks` shim (execs the
gate, no self-check) then re-pinned. No re-vendor was needed: every repo pins the dispatcher by
absolute path, so one Tools commit fixed it machine-wide and the census stayed canonical.
`hooks_selftest.py` rows 6-10 pin the behavior. Full record: `gate_evidence.json` EV-043.
