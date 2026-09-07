# DOCS_VERSIONS.md - version register for the gate documentation

> **Doc version: 1.1 - 2026-09-07.** New at 1.0; 1.1 registers the EV-043 doc release. This file is the authoritative register of every
> gate-related document, its current version, and what changed at each version. Each tracked
> doc carries a `Doc version: N.N - DATE` line in its own header that must match its row here.

## How versioning works

- **Major (N.0):** the doc's model of the system changed - a subsystem was added, a claim was
  retracted, or a large section was rewritten. A reader who knew the previous major must
  re-read.
- **Minor (N.n):** additions, corrections, or clarifications that do not change the model - a
  new command flag, a fixed count, a new cross-reference.
- A **docs release** groups the version bumps made together for one reason (a feature, a
  filing). Releases are listed newest-first in the changelog below.

## Current versions

### colibri-code-review/docs

| Doc | Version | Status |
|---|---|---|
| [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md) | 1.1 | machine-wide arming: dispatcher dir, absolute pin, census, HOOK_NAMES + rules epoch; EV-043 hardening section |
| [CODEX_GATE_IMPLEMENTATION.md](CODEX_GATE_IMPLEMENTATION.md) | 1.1 | step-by-step gate implementation for Codex + the `decide()` audit; §3.5 partial commits + EV-043 |
| [ADVERSARY_GATE.md](ADVERSARY_GATE.md) | 2.0 | the wall; arming section now machine-wide; code-class includes hook-name files |
| [HARNESS_GUARD.md](HARNESS_GUARD.md) | 2.0 | layer 2 `decide()` catalogue, with the 2026-09-06 arming-side rules |
| [LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md) | 2.0 | the four layers; layer 0 is now the dispatcher, armed machine-wide |
| [GATE_INSTALLER.md](GATE_INSTALLER.md) | 2.0 | installer reference; absolute pin, census, epoch, reanchor |
| [GATE_ADOPTION_PLAYBOOK.md](GATE_ADOPTION_PLAYBOOK.md) | 2.0 | adoption runbook; hook-name code class, dispatcher layer 0 |
| [EXTERNAL_SUBAGENT.md](EXTERNAL_SUBAGENT.md) | 1.1 | machine prerequisites; machine-wide arming note |
| [ISSUE_90887_FILING.md](ISSUE_90887_FILING.md) | 2.2 | the anthropics/claude-code#90887 archive; Version 2 POSTED (issuecomment-5570626121) |
| [ISSUE_SKILL_GATE_FILING.md](ISSUE_SKILL_GATE_FILING.md) | 1.1 | the G38 skill-gate post; POSTED as issue #92656 |
| [GATE_EVIDENCE_DOCKET.md](GATE_EVIDENCE_DOCKET.md) | (docket) | human view of `gate_evidence.json`; through EV-043 |
| gate_evidence.json | (docket) | machine-readable evidence docket; 43 entries, through EV-043 |
| [DOCS_VERSIONS.md](DOCS_VERSIONS.md) | 1.1 | this register |

Docs about the colibri review tool itself (not the gate) are unversioned here and unchanged
by the gate releases: README.md, BATCH.md, CONSOLE.md, MODES.md, SPEC_AUTHORING.md,
STATIC_SIGNALS.md, STORAGE.md, GATE_SWEEP_2026-09-02_*_PENDING.md.

### Tools repo (gate source, versioned alongside)

| Doc | Version | Status |
|---|---|---|
| `TOOLS_MANIFEST.md` | (rolling) | the tool register; adversary-gate row = machine-wide arming |
| `adversary-gate/CODEX_INTEGRATION.md` | 2.0 | pointer to CODEX_GATE_IMPLEMENTATION.md + the single-source rule |
| `adversary-gate/GUARD_PORTABILITY.md` | (rolling) | guard portability notes |
| `arm-repo/README.md` | 1.1 | the new-repo arming protocol; `--census` passthrough, exact-value verify |
| `skill-gate/README.md` | (rolling) | G38 skill gate |

## Changelog

### Filings posted 2026-09-07

The two drafts were posted to anthropics/claude-code from the owner's gh account, and their URLs
recorded (posted text archived verbatim, never overwritten):

- **ISSUE_90887_FILING.md 2.1 -> 2.2** - Version 2 evidence posted as
  <https://github.com/anthropics/claude-code/issues/90887#issuecomment-5570626121>.
- **ISSUE_SKILL_GATE_FILING.md 1.0 -> 1.1** - posted as its own issue
  <https://github.com/anthropics/claude-code/issues/92656>.

### Docs release 2026-09-07 (later) - EV-043 dispatcher self-check hardening

Landing the "universal arming" release below - a partial commit under the stage-explicit-paths
discipline - exposed a defect in the machine-wide dispatcher self-check (it false-fired on every
partial commit, and its in-band exception leaked a hole in three straight gate review rounds).
Fixed in Tools `7ba0e3b` (strictly fail-closed self-check + a clean-git-context helper); docketed
as EV-043. Doc changes:

- **UNIVERSAL_ARMING.md 1.0 -> 1.1** - added the "Post-rollout hardening: EV-043" section.
- **CODEX_GATE_IMPLEMENTATION.md 1.0 -> 1.1** - added §3.5 (partial commits, and how to commit a
  dispatcher edit through the `.githooks` shim).
- **ISSUE_90887_FILING.md 2.0 -> 2.1** - EV-043 added to the Version 2 draft (the gate BLOCKing
  its own repair twice is the sharpest restatement of the thesis).
- **gate_evidence.json / GATE_EVIDENCE_DOCKET.md** - EV-043 added (43 entries); scoreboard bumped.
- **DOCS_VERSIONS.md 1.0 -> 1.1** - this entry and the register rows above.

### Docs release 2026-09-07 - universal arming + Codex implementation

The machine-wide arming tranche (Tools commits `1332bff`, `cde796d`, `40c25f7`, `e61d8a4`,
`a349374`; nine repos re-vendored) landed the night of 2026-09-06/07. This docs release
brings every gate doc up to that architecture and adds the Codex-side and versioning docs.

- **NEW UNIVERSAL_ARMING.md 1.0** - the dispatcher hook dir, the global value + per-repo
  absolute pin, the census and its states, HOOK_NAMES, the rules epoch and its history
  anchoring, and the ~17-round hardening record.
- **NEW CODEX_GATE_IMPLEMENTATION.md 1.0** - the step-by-step Codex gate implementation (the
  plugin, `hooks.json`, `codex_guard.py`, the single-source rule, worktrees), and a full audit
  and explanation of `decide()` (verdict: sound, documented residuals, no code change).
- **NEW ISSUE_SKILL_GATE_FILING.md 1.0** - a draft filing/post for the G38 skill gate.
- **NEW DOCS_VERSIONS.md 1.0** - this register.
- **ADVERSARY_GATE.md 1 -> 2.0** - the "arming per clone" section replaced with machine-wide
  arming; hook-name files added to the code class; selftest counts refreshed.
- **HARNESS_GUARD.md 1 -> 2.0** - the arming-side Bash rules (global/config/env denials, the
  dispatcher-dir covenant, the two arming spellings, 8.3 aliases, the two-view de-quoting) and
  the `decide()` residuals; selftest count 148 -> 231.
- **LAYERED_ENFORCEMENT.md 1 -> 2.0** - layer 0 is the dispatcher armed machine-wide; layer 3
  gains HOOK_NAMES and the rules epoch; residual 4 retraction kept (EV-041).
- **GATE_INSTALLER.md 1 -> 2.0** - the absolute pin, `--census`, the epoch and `--reanchor-epoch`,
  the dispatcher; exit-code and count refresh.
- **GATE_ADOPTION_PLAYBOOK.md 1 -> 2.0** - the code class includes hook-name files; layer 0 is
  the dispatcher; verification checklist updated.
- **EXTERNAL_SUBAGENT.md 1 -> 1.1** - machine-wide arming note in prerequisite 5.
- **ISSUE_90887_FILING.md 1 -> 2.0** - Version 2 evidence appended (never overwriting Version 1):
  universal arming, ~17 additional blocked rounds on the gate's own code, EV-041/EV-042.
- **gate_evidence.json / GATE_EVIDENCE_DOCKET.md** - EV-041 (arming residual accepted on a false
  git premise) and EV-042 (the canonical shims were never gated code) added 2026-09-06.
- **Tools CODEX_INTEGRATION.md 1 -> 2.0**, **arm-repo/README.md -> 1.1** - see their rows.

### Prior state (pre-2026-09-07)

The gate docs were authored 2026-08-30 (ADVERSARY_GATE, GATE_INSTALLER) through 2026-09-04
(HARNESS_GUARD, the EV-028..030 arc) with rolling in-place edits and no formal version line.
This release introduces the version lines; treat everything before it as "version 1" of each
doc.
