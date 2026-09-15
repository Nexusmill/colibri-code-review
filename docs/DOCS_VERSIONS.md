# DOCS_VERSIONS.md - version register for the gate documentation

> **Doc version: 1.6 - 2026-09-15.** New at 1.0; 1.1 registers the EV-043 doc release; 1.2 the EV-045/046 release; 1.3 the 2026-09-14 re-baseline on Tools 6773f97; 1.4 the docket extent EV-085; 1.5 EV-086 (the docs lane refused this release's own landing - fixed in Tools 51ba4b3); 1.6 EV-087 (the gate's own transport crash - fixed in Tools 26280c7). This file is the authoritative register of every
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
| [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md) | 1.2 | machine-wide arming: dispatcher dir, absolute pin, census, HOOK_NAMES + rules epoch; EV-043 hardening section; 1.2 = armed at birth (ROOT), the relocated-suite state, two EV-043-superseded claims corrected |
| [CODEX_GATE_IMPLEMENTATION.md](CODEX_GATE_IMPLEMENTATION.md) | 1.2 | step-by-step gate implementation for Codex + the `decide()` audit; §3.5 partial commits + EV-043; 1.2 = §2.6 the reviewed-write broker + enforcement server (EV-060, 6773f97), auto-review in §3.3 |
| [ADVERSARY_GATE.md](ADVERSARY_GATE.md) | 3.0 | the wall; 3.0 = auto-review on commit (the loop changed), the fallback model chain, the docs lane's evidence gate, the removed-symbol refusal (EV-060), armed at birth (EV-055), owner tools, current selftest inventory |
| [HARNESS_GUARD.md](HARNESS_GUARD.md) | 2.1 | layer 2 `decide()` catalogue, with the 2026-09-06 arming-side rules; 2.1 = field over-denies recorded, plugin sync note |
| [LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md) | 2.2 | the four layers; layer 0 is the dispatcher; 2.1 = the push-time secret barrier and the fixture skip; 2.2 = auto-review + removed-symbol refusal at layer 0, ROOT baseline + auditor hardening + notes scrubber at layer 3, evidence-gated docs lane, `owner_ff_merge` at layer 4 |
| [GATE_INSTALLER.md](GATE_INSTALLER.md) | 2.1 | installer reference; absolute pin, census, epoch, reanchor; 2.1 = ROOT at birth, the proving sequence under auto-review, 73/73 |
| [GATE_ADOPTION_PLAYBOOK.md](GATE_ADOPTION_PLAYBOOK.md) | 3.0 | adoption runbook; 3.0 = the proof is the gate line not a refusal, the auto-review loop, code class + docs lane, model chain, landing by `owner_ff_merge`, new troubleshooting entries |
| [EXTERNAL_SUBAGENT.md](EXTERNAL_SUBAGENT.md) | 1.2 | machine prerequisites; machine-wide arming note; 1.2 = git PATH fallback, the optional docs-lane model, the marketplace plugin as the no-Tools-clone distribution |
| [ISSUE_90887_FILING.md](ISSUE_90887_FILING.md) | 2.2 | the anthropics/claude-code#90887 archive; Version 2 POSTED (issuecomment-5570626121) - an archive of posted text, deliberately NOT re-baselined |
| [ISSUE_SKILL_GATE_FILING.md](ISSUE_SKILL_GATE_FILING.md) | 1.1 | the G38 skill-gate post; POSTED as issue #92656 |
| [GATE_EVIDENCE_DOCKET.md](GATE_EVIDENCE_DOCKET.md) | (docket) | human view of `gate_evidence.json`; through EV-087 |
| gate_evidence.json | (docket) | machine-readable evidence docket; 87 entries, through EV-087 |
| [DOCS_VERSIONS.md](DOCS_VERSIONS.md) | 1.6 | this register |

Docs about the colibri review tool itself (not the gate) are unversioned here and unchanged
by the gate releases: README.md, BATCH.md, CONSOLE.md, MODES.md, SPEC_AUTHORING.md,
STATIC_SIGNALS.md, STORAGE.md, GATE_SWEEP_2026-09-02_*_PENDING.md.

### Tools repo (gate source, versioned alongside)

| Doc | Version | Status |
|---|---|---|
| `TOOLS_MANIFEST.md` | (rolling) | the tool register; adversary-gate row = machine-wide arming + the 2026-09-14 addendum (model chain, docs lane, secrets policy, ROOT, removed-symbol refusal, owner tools, plugin 0.3.0, counts); new rows arm-repo + the Codex enforcement broker |
| `adversary-gate/CODEX_INTEGRATION.md` | 2.1 | pointer to CODEX_GATE_IMPLEMENTATION.md + the single-source rule; 2.1 = the reviewed-write broker, EV-060, the restart rule |
| `adversary-gate/GUARD_PORTABILITY.md` | (rolling) | guard portability notes |
| `arm-repo/README.md` | 1.2 | the new-repo arming protocol; `--census` passthrough, exact-value verify; 1.2 = layer 5 repo-memory, `--skip-memory`, the UTF-8 pipe fix, 23 rows |
| `skill-gate/README.md` | (rolling) | G38 skill gate |
| `colibri-marketplace/plugins/adversary-gate/README.md` + `SKILL.md` | 0.3.0 (plugin) | the distributed copy's docs; re-baselined 2026-09-14 with the payload |

## Changelog

### Docket 2026-09-15 - EV-087, the gate's own transport crash (Tools 26280c7)

No gate doc changed. The docket grew by one row from the fleet atlas leg: the gate crashed on a
truncated model response (`http.client.IncompleteRead` escaped an `OSError`-only handler - no failover,
no verdict), fixed the same session in Tools 26280c7 under TDD (callmodel_selftest 4/6 -> 6/6, gate
CLEAR round 1). Tools main carries the fix LOCALLY (push held for the owner); the hooks run the working
tree. The marketplace plugin's `adversary_gate.py` is now two Tools commits behind (51ba4b3, 26280c7) -
the 0.3.2 re-vendor covers both.

- **gate_evidence.json / GATE_EVIDENCE_DOCKET.md** - EV-087 added (87 entries); scoreboard bumped.
- **DOCS_VERSIONS.md 1.5 -> 1.6** - this entry.

### Docs release 2026-09-14 - re-baseline on Tools 6773f97 (a week of gate changes, one pass)

Owner order 2026-09-14 ("make sure they are current with everything we've done and changed,
and increment the versions of the docs you change"). Between the 09-07 evening release and
Tools 6773f97 the gate gained: auto-review on commit (9597241 - the hook requests the review;
"commit REFUSED - lacks a fresh clearance" is no longer reachable from a commit), the
docscan evidence gate and its four false-positive fixes (f2fdfd4, 724d095, 14d1f09, fb0d9a6,
d9876ff) plus the published-commit exclusion (6d24c55), `owner_ff_merge.py` (ae014e0,
15555dd, a5ca6b7), `owner_scrub_notes.py` (b01c8fb), armed at birth (9e46976, 83b45f1) and
the auditor's ref-deletion / shallow hardening (3c1243a, 70835b6), the restored secret
wrapper + removed-symbol refusal (de3f953, EV-060), the reviewer-prompt manifest doctrine
(8db2fbe), the broker's bounded BLOCK reason (6773f97), and arm-repo's layer 5 (40a848e,
a0683c3). The same day the marketplace plugin was re-vendored to those bytes (0.3.0) and the
docket reached EV-084. Every claim below was re-verified against the Tools bytes or a live run
before it was written; selftest counts are from runs on 2026-09-14.

- **ADVERSARY_GATE.md 2.1 -> 3.0**, **GATE_ADOPTION_PLAYBOOK.md 2.0 -> 3.0** - the model of the
  loop changed (auto-review), so major.
- **LAYERED_ENFORCEMENT.md 2.1 -> 2.2**, **GATE_INSTALLER.md 2.0 -> 2.1**,
  **UNIVERSAL_ARMING.md 1.1 -> 1.2**, **HARNESS_GUARD.md 2.0 -> 2.1**,
  **CODEX_GATE_IMPLEMENTATION.md 1.1 -> 1.2**, **EXTERNAL_SUBAGENT.md 1.1 -> 1.2** - additions
  and corrections (details in the table above).
- **Tools:** `adversary-gate/CODEX_INTEGRATION.md 2.0 -> 2.1`, `arm-repo/README.md 1.1 -> 1.2`,
  `TOOLS_MANIFEST.md` addendum + two rows; `install_gate.py`'s printed NEXT steps now describe
  the auto-review proof (a gated code change in Tools).
- **Docket:** through EV-085 (EV-085 = the gate round on the Tools half of this very release, added the same evening).
- **DOCS_VERSIONS.md 1.2 -> 1.3** - this entry; **1.3 -> 1.4** the EV-085 extent; **1.4 -> 1.5** the EV-086 extent (the owner's landing of this very release was refused by the docs lane; Tools 51ba4b3) - same release day.

### Docs release 2026-09-07 (evening) - EV-045 fixture skip, EV-046 warn / scrub / refuse-at-push

Owner rulings of 2026-09-07 landed in Tools as three gated commits (1f287bb, 8245433,
ad484fa; ten gate rounds in all, every BLOCK a real leak path or blindness - docket EV-047):

- **ADVERSARY_GATE.md 2.0 -> 2.1** - new "Secrets" section: the fixture-repository skip, warn
  + scrub at commit, the push-time barrier, the receipts.
- **LAYERED_ENFORCEMENT.md 2.0 -> 2.1** - the secrets paragraph under the notes machinery.
- **gate_evidence.json / GATE_EVIDENCE_DOCKET.md** - EV-045 and EV-046 closed in place with
  their fix commits; EV-047 added (the gate reviewing its own scrub and push guard).
- **DOCS_VERSIONS.md 1.1 -> 1.2** - this entry.

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
