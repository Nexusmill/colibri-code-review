# LAYERED_ENFORCEMENT.md - the four layers around the adversarial commit gate

> **Doc version: 2.2 - 2026-09-14.** See [DOCS_VERSIONS.md](DOCS_VERSIONS.md). Layer 0 is now a
> **dispatcher**, armed **machine-wide**; layer 3 gained HOOK_NAMES and the rules epoch. Full
> architecture: [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md). 2.1: fixture repositories under
> the profile Temp skip the layer-0 review (EV-045); secrets warn and are scrubbed at commit
> and are refused by the push guard (EV-046) - [ADVERSARY_GATE.md](ADVERSARY_GATE.md) § Secrets.
> 2.2 (Tools 6773f97): layer 0 requests the review itself and refuses removed symbols with
> live callers before any model call; layer 3 is armed at birth (ROOT baseline) with the
> auditor's ref-deletion and shallow-history hardening, and gained the owner's notes scrubber;
> the docs lane has an evidence gate; layer 4 lands protected branches with `owner_ff_merge.py`.
>
> Added 2026-08-31 after the owner's observation that the gate is *git-centered*: a
> pre-commit hook is advisory by construction, and git offers many ways around it
> (`--no-verify`, `-n`, re-pointing `core.hooksPath`, plumbing via
> `commit-tree`/`update-ref`, GUI no-verify commands, an unarmed fresh clone). Worse,
> the trivial bypass is not a flag at all: an agent could compute the staged sha256s and
> **write `.adversary/clearance.json` directly** - forging the clearance the hook
> checks. This document defines the layered answer. Sources of truth:
> `Tools/adversary-gate/` (gate, installer, auditor, harness guard).

## The honest claim

**No client-side scheme can prevent; it can only raise the cost and make bypass
detectable.** A human at a shell always wins - and that is fine, because the one-shot
OVERRIDE is the owner's anyway. The layers only need to be airtight against *agents
operating through the harness*, plus detection for everything else:

| Layer | Where | Mechanism | Stops |
|---|---|---|---|
| 0 (the wall) | pre-commit / post-commit / pre-push **dispatcher** hooks, armed **machine-wide** by the global `core.hooksPath` (owner-set) + a per-repo absolute pin | each dispatcher self-checks, runs `adversary_gate.py check`/`record`/`check-push`, then the repo's own default-dir hook. Since Tools 9597241 (2026-09-07) `check` REQUESTS the review itself when staged code lacks a fresh clearance (auto-review on commit; `run --context` is the explicit review/rebuttal interface), and since de3f953 (EV-060) `run` refuses - deterministically, before any model call - a staged `.py` that removes a module-level symbol a tracked unstaged `.py` still references | ordinary ungated commits, in every checkout and worktree on the machine ([UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md)) |
| 1 | commit driver (`_git_do.py`, Nexusmill) | runs `check` directly before commit, `record` after | disarmed-clone commits through the driver |
| 2 | Claude Code / Codex PreToolUse hook | `harness_guard.py` (Codex via `codex_guard.py`) denies bypass + forgery commands | the agent-reachable workarounds |
| 3 (the catch-all) | post-commit notarization + auditor | durable git notes on `refs/notes/adversary`; `adversary_audit.py` re-verifies every commit | EVERYTHING, after the fact |
| 4 | CI + branch protection | vendored auditor in GitHub Actions; required check on `main` | bypass reaching the shared remote |

Layer 0 was a single per-clone `pre-commit` hook until 2026-09-06; it is now three dispatcher
shims armed machine-wide. The [census](UNIVERSAL_ARMING.md#the-census-install_gatepy---census-root-)
proves every checkout and worktree.

## Layer 3 - the tripwire (the load-bearing layer)

Clearances are transient (`.adversary/clearance.json`, gitignored). Durability comes
from **git notes**: after every commit, `adversary_gate.py record` (wired as the
`post-commit` hook, and also called by the Nexusmill driver) writes a JSON note on
`refs/notes/adversary` **iff** every changed code blob in HEAD matches a fresh CLEAR row
- embedding the reviewer's artifact text as evidence. `record` is **fail-closed**: on
any mismatch it writes *nothing*, because the ABSENCE of a note is exactly the signal.

`adversary_audit.py` walks every commit after the baseline (`.githooks/
adversary_baseline`, written at install time - earlier commits were gated but their
clearances were transient, so auditing them would be pure false alarms; since 2026-09-08 a
repo armed EMPTY gets the baseline `ROOT` and every commit including the root is walked -
"armed at birth", Tools 9e46976, EV-055), recomputes each changed blob's sha256 with the same
path rules as the gate, and demands a matching CLEAR note. No note, a missing path, or a sha
mismatch = **VIOLATION**. Owner OVERRIDE commits carry an OVERRIDE note with the recorded
reason - listed loudly, passing by default, violations under `--strict-override`. The auditor
is **self-contained and vendored** into each repo's `.githooks/` so CI needs no external
tooling; a parity selftest asserts its duplicated path rules never drift from the gate's. Two
catches hardened its ROOT path in the field (EV-063 / EV-064, Tools 3c1243a / 70835b6): a
deleted current-branch ref no longer lets a ROOT repository with remaining commits read clean
(object enumeration must succeed and find no commits; corrupt or hidden refs fail closed), and
the ROOT epoch shortcut probes shallow history first.

Notes are evidence, and evidence can carry what the reviewer quoted: a value the reviewer SAW
can sit in `refs/notes/adversary` after the tree was scrubbed, and neither the push guard
(which never scans notes) nor an agent (the harness guard forbids touching notes) can remove
it. `owner_scrub_notes.py` (Tools b01c8fb) is the owner-only scrub of a value class out of
the notes: orphan-rebuilt ref, unreachable notes pruned, the auditor re-verified, dry run by
default.

Machinery that keeps notes honest across history rewrites: the installer sets
`notes.rewriteRef refs/notes/adversary`, so amend/rebase copy notes to rewritten
commits - unchanged blobs keep their valid clearance, conflict-resolved blobs correctly
flag. **When pushing, push the notes too:** `git push origin refs/notes/adversary`.

Secrets (owner rulings 2026-09-07, EV-045/EV-046): layer 0 no longer blocks a commit on a
secret-shaped hit - it warns, scrubs every matched value out of the review payload, and hands
the enforcement to the pre-push dispatcher, which scans every outgoing commit's added lines
and refuses a push carrying a secret literal (heuristic hits warn; outgoing docs re-run
through the local docs model). Fixture repositories under the profile Temp skip the layer-0
review entirely but never the push guard. The docs model's block is EVIDENCE-GATED (Tools
f2fdfd4 and its four follow-ups, 2026-09-07..09): it stands only when the model's REASON line
quotes a value - names, placeholders, role words and elided prefixes withdraw it, loudly - and
the docs feed excludes commits already on the remote's tracking refs, so a fresh branch never
re-feeds published history (EV-061). The remaining known false-positive class - a
provider/model slug held as a value - is EV-083, with the Tools fix owed.

OVERRIDE provenance: consuming `.adversary/OVERRIDE` snapshots the staged shas into
`override_used.json`; `record` converts it to an OVERRIDE note only while HEAD carries
those exact blobs - a lingering override file cannot bless a later commit.

**HOOK_NAMES + the rules epoch (2026-09-06, EV-042).** The extensionless hook files
(`pre-commit`, `post-commit`, `pre-push`) are the single source of every vendored shim and had
never been gated code. The gate and the vendored auditor now classify them as code wherever
they live, confined to commits after a per-repo `.githooks/adversary_rules_epoch` - read from
HEAD's tree only and anchored so the recorded sha must be an ancestor of every commit that ever
added it (a moved, uncommitted, shallow or unreadable epoch fails closed). Details and the
`--reanchor-epoch` recovery: [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md#hook_names-hook-files-are-code-wherever-they-live-ev-042).

## Layer 2 - the harness guard

`Tools/adversary-gate/harness_guard.py`, registered as a Claude Code PreToolUse hook
(matcher `Bash|Write|Edit|NotebookEdit`), denies with a G39 explanation: any git
`--no-verify` / `commit -n`; `hooksPath` changes except arming (`.githooks`);
`commit-tree`; `update-ref`; mutating `git notes` subcommands; **any write to
`.adversary/**` via file tools or Bash** (the forgery route - the gate's own writes run
as subprocesses inside git hooks, invisible to PreToolUse, so nothing legitimate
breaks); `ADVERSARY_FAKE` outside selftests. It fails OPEN on malformed input - the wall
and the tripwire stand behind it. Accepted false positive: `--no-verify` inside a quoted
commit message still blocks; reword.

Since 2026-09-04 it also refuses **any reference to the live hook dir `.git/hooks`** (any
spelling, no read exemption - the tracked `.githooks/` shim never matches), the G38 skill
gate's state dir `skill_gate/`, and a variable-built `$VAR commit -n`; `git commit -mn msg`
(a value-taking bundle, the hook runs) is no longer a false positive; and file-tool paths are
canonicalised with every ambiguous dot/space segment read both ways before the compare. The
full rule catalogue, the seven-round hardening arc (EV-028 to EV-030) and the Caliper twin are
in `HARNESS_GUARD.md`. Since 2026-09-06 it also denies every agent write of a global/system
hooks value and every literal-free config write that could re-point it, guards the machine-wide
dispatcher dir like `.git/hooks`, admits the second arming spelling (the absolute dispatcher
dir), and judges each Bash segment in a de-quoted view too.

## Layer 4 - CI + branch protection

`.github/workflows/adversary-audit.yml` (fetch-depth 0, fetch the notes ref, run the
vendored auditor) in every repo with a GitHub remote; branch protection requires the
`audit` check on `main`. `.github/workflows/` is itself in the gate's GATED path set -
the same class of hole as `.githooks/` edits (birth review r2): enforcement config never
changes without an independent CLEAR.

A protected branch therefore only ever moves by fast-forwarding a sha that ALREADY passed
the `audit` check on a side branch - a direct push of local `main` is rejected by GitHub
("Required status check audit is expected"), and the UI merge button (squash-only under
linear history) would mint one unaudited sha. `Tools/adversary-gate/owner_ff_merge.py`
(2026-09-07) is the owner's landing tool: it verifies the PR is open and mergeable, that
origin/main is an ancestor, and that a successful `audit` check-run exists for the exact
head sha, then pushes that sha to `main` through the armed pre-push guard and deletes the
remote side branch (`--only <repo> --pr N --head <branch> --apply`; dry run without
`--apply`).

## Known residual risks (documented, not hidden - G1/G11)

1. **Note forgery by a determined fraudster**: a note with correct shas and fabricated
   verdict text passes the auditor. The recorded artifact text makes fraud *checkable*
   (re-run a review against the same bytes); detection, not prevention, by design.
2. **The guard is regex over command strings**: exotic encodings or nested interpreters
   can evade it. Layer 3 catches what slips through.
3. **Notes live in the repo**: deleting `refs/notes/adversary` locally orphans evidence;
   the auditor then reports violations (fail-noisy), and the pushed copy survives on the
   remote once layer 4 is active.
4. ~~**Unarmed fresh clones** still commit locally un-gated (per-clone arming is a git
   limitation); their commits carry no notes and fail the audit at push time.~~
   **RETRACTED 2026-09-06 (EV-041, caught by the owner while setting up Codex):** the premise
   was false - a machine-global `core.hooksPath` arms a fresh init, clone and worktree with no
   per-clone action (probed with real git under a temp global config). Worse, and live:
   worktrees of ARMED repos on branches without `.githooks/` were committing un-gated - the
   relative value dangled and git ran no hook (two cases on the owner's machine). Arming is now
   MACHINE-WIDE: git's global hook path is the canonical dispatcher dir
   `Tools/adversary-gate/hooks` (owner-set; gate first, then the repo's own default-dir hook)
   and `install_gate.py` pins the same ABSOLUTE value per repo; `install_gate.py --census`
   proves every checkout and worktree (`armed | dangling | unset | overridden`). A never-installed
   repo is gated at commit immediately; its first push of old un-notarized code is refused until
   the installer writes the baseline. Other machines and CI keep the per-clone recipe.
