# LAYERED_ENFORCEMENT.md - the four layers around the adversarial commit gate

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
| 0 (the wall) | pre-commit hook | `adversary_gate.py check` | ordinary ungated commits |
| 1 | commit driver (`_git_do.py`, Nexusmill) | runs `check` directly before commit, `record` after | disarmed-clone commits through the driver |
| 2 | Claude Code PreToolUse hook | `harness_guard.py` denies bypass + forgery commands | the agent-reachable workarounds |
| 3 (the catch-all) | post-commit notarization + auditor | durable git notes on `refs/notes/adversary`; `adversary_audit.py` re-verifies every commit | EVERYTHING, after the fact |
| 4 | CI + branch protection | vendored auditor in GitHub Actions; required check on `main` | bypass reaching the shared remote |

## Layer 3 - the tripwire (the load-bearing layer)

Clearances are transient (`.adversary/clearance.json`, gitignored). Durability comes
from **git notes**: after every commit, `adversary_gate.py record` (wired as the
`post-commit` hook, and also called by the Nexusmill driver) writes a JSON note on
`refs/notes/adversary` **iff** every changed code blob in HEAD matches a fresh CLEAR row
- embedding the reviewer's artifact text as evidence. `record` is **fail-closed**: on
any mismatch it writes *nothing*, because the ABSENCE of a note is exactly the signal.

`adversary_audit.py` walks every commit after the baseline (`.githooks/
adversary_baseline`, written at install time - earlier commits were gated but their
clearances were transient, so auditing them would be pure false alarms), recomputes each
changed blob's sha256 with the same path rules as the gate, and demands a matching CLEAR
note. No note, a missing path, or a sha mismatch = **VIOLATION**. Owner OVERRIDE commits
carry an OVERRIDE note with the recorded reason - listed loudly, passing by default,
violations under `--strict-override`. The auditor is **self-contained and vendored** into
each repo's `.githooks/` so CI needs no external tooling; a parity selftest asserts its
duplicated path rules never drift from the gate's.

Machinery that keeps notes honest across history rewrites: the installer sets
`notes.rewriteRef refs/notes/adversary`, so amend/rebase copy notes to rewritten
commits - unchanged blobs keep their valid clearance, conflict-resolved blobs correctly
flag. **When pushing, push the notes too:** `git push origin refs/notes/adversary`.

OVERRIDE provenance: consuming `.adversary/OVERRIDE` snapshots the staged shas into
`override_used.json`; `record` converts it to an OVERRIDE note only while HEAD carries
those exact blobs - a lingering override file cannot bless a later commit.

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

## Layer 4 - CI + branch protection

`.github/workflows/adversary-audit.yml` (fetch-depth 0, fetch the notes ref, run the
vendored auditor) in every repo with a GitHub remote; branch protection requires the
`audit` check on `main`. `.github/workflows/` is itself in the gate's GATED path set -
the same class of hole as `.githooks/` edits (birth review r2): enforcement config never
changes without an independent CLEAR.

## Known residual risks (documented, not hidden - G1/G11)

1. **Note forgery by a determined fraudster**: a note with correct shas and fabricated
   verdict text passes the auditor. The recorded artifact text makes fraud *checkable*
   (re-run a review against the same bytes); detection, not prevention, by design.
2. **The guard is regex over command strings**: exotic encodings or nested interpreters
   can evade it. Layer 3 catches what slips through.
3. **Notes live in the repo**: deleting `refs/notes/adversary` locally orphans evidence;
   the auditor then reports violations (fail-noisy), and the pushed copy survives on the
   remote once layer 4 is active.
4. **Unarmed fresh clones** still commit locally un-gated (per-clone arming is a git
   limitation); their commits carry no notes and fail the audit at push time.
