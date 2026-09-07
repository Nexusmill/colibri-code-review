# ISSUE_SKILL_GATE_FILING.md - draft post: structural enforcement of skill routing (G38)

> **Doc version: 1.1 - 2026-09-07.** See [DOCS_VERSIONS.md](DOCS_VERSIONS.md). POSTED 2026-09-07
> as its own issue: <https://github.com/anthropics/claude-code/issues/92656> - about the G38
> skill gate: the same "only the harness can make a tool call conditional on prior state"
> argument, applied to skill/process-routing rather than commit review. Source of truth:
> `Tools/skill-gate/` and `Nexusmill/docs/superpowers/specs/2026-09-04-skill-gate-design.md`.
> Archived verbatim below - never overwritten.

---

## The problem: a routing mandate that instructions alone did not enforce

Claude Code (and Cowork) can be given a skill-routing policy: for a class of task, load a
particular process skill before acting. Ours (rule G38) is explicit - a bug routes through
systematic-debugging or a review skill; any coding takes the karpathy-guidelines posture; a
change that is "done" runs verification-before-completion before the claim or the commit; and so
on. The policy lived in the operating instructions.

**A tool-generated census showed the policy was almost entirely ignored.** Over one month,
across ~2,800 source edits, `verification-before-completion` ran **zero** times;
`karpathy-guidelines` ran **twice**; only one process skill (a code-review skill) had real
adoption. This is the same failure mode as the commit-review issue: an instruction that asks the
agent to do something before acting is not enforced by anything, and under time pressure it is
skipped - and, exactly as with self-review, the agent will often report the work as done
*without* the verification the instruction asked for. Measuring adoption by census, not by
belief, is what surfaced it (the earlier belief was that the skills "were being used").

## What we built (userland), and its honest limits

`skill-gate` is a set of PreToolUse / PostToolUse / Stop hooks that keep a per-session ledger of
which skills have actually been invoked, and **DENY** the gated tool call until the required
skill for that situation is on record:

| Gate | Fires on | Released by |
|---|---|---|
| POSTURE | the first source edit of the session | `karpathy-guidelines` + one process-entry skill invoked this session |
| BUGROUTE | a source edit after a failure appeared in tool output | a debugging/review skill invoked *after* the failure |
| SAFEWRITE | a harness Edit/Write on a tracked repo file | (never - use the truncation-safe write tools, which are not gated by this row) |
| COMMIT | a git commit / gate-run shell call | `verification-before-completion` invoked after the last source edit |
| Stop | ending a turn with unverified edits | `verification-before-completion` (one block per turn) |

It works: within its first days it forced the process skills to actually run before edits and
commits, and its own wiring change and the desktop-host (Cowork) coverage were themselves
hardened by the adversarial commit gate (the wiring is tracked code, so it goes through review
like anything else - which caught a bootstrap that would have hard-blocked every gated tool in
every wired repo on a missing script, and a `sys.path` poisoning where a repo shipping `json.py`
would have run inside the gate process).

**The limits are the same as the commit gate's, and they point the same way:**

- The gate binds agents *inside the harness*. A human at a shell is not gated - and that is
  fine.
- It is fail-open: any hook error allows the call. A hook cannot be allowed to brick the session,
  so a broken gate degrades to "no gate," and the census is the backstop that would show it.
- Writes routed *through* the Bash tool (`sed -i`, `cat >`, `git apply`) and commit paths other
  than `commit` (`merge`, `rebase --continue`) are outside the tool matchers by construction; the
  census, again, is the only thing that would catch an agent routing around the gate that way.
- Subagent delegation is handled (a subagent's edit resolves to its parent session's ledger), but
  only because we could reconstruct the parent from the transcript path - a harness-native
  mechanism would not need that reverse-engineering.

## The ask (same shape as #90887)

The only fully trustworthy place to make a tool call **conditional on prior session state** -
"this edit is blocked until skill X ran this session," "this turn cannot end until verification
ran since the last edit" - is the harness itself. Userland hooks can *approximate* it (and ours
does, measurably), but they are advisory-by-construction, fail open, and cannot see the tool
calls the harness does not route through a matcher. A first-class harness capability to gate a
tool call on a declared precondition (a skill invoked, a check run, a prior verdict) would make
routing enforcement as reliable as the platform's own permissions - and it composes directly
with the commit-review capability requested in #90887: the same "make this tool call conditional
on evidence" primitive serves both.

Success for the userland version is measured, not asserted: the month after the gate went live is
a census window, and the proof is the adoption numbers moving - not a claim that the skills are
now used. That measurement discipline is itself the lesson: mandates are followed in proportion
to how they are *enforced and counted*, not how firmly they are *stated*.

The skill-gate suite (hooks, installer, selftests) ships alongside the adversary-gate suite and
is MIT. Full design: `Tools/skill-gate/README.md` and the design spec cited above.
