# ISSUE_90887_FILING.md - the posted evidence comment on anthropics/claude-code#90887

> The comment below was POSTED 2026-09-01 (owner's order, posted from the owner's gh
> account by the session agent): 
> <https://github.com/anthropics/claude-code/issues/90887#issuecomment-5503762795>
> This file is the permanent archive of the exact posted text (standing owner rule
> 2026-09-01: outward-facing deliverables are never drafted-and-left in a gitignored
> junk/ dir - they get a tracked home). Companions: gate_evidence.json (the docket the
> comment tabulates), LAYERED_ENFORCEMENT.md and GATE_ADOPTION_PLAYBOOK.md (embedded in
> the comment verbatim). If the filing is ever amended and re-posted, append the new
> version below with its comment URL - never overwrite a posted version.

---

## Version 1 - posted 2026-09-01, issuecomment-5503762795

**Update (2026-09-01): we built a full userland implementation of this proposal and have been running it in production for ~2.5 days across nine armed repos and ~68 gated commits since filing.** Appending the two reference documents below (threat model + adoption playbook, unchanged) after a refreshed evidence tally. Everything below is drawn from a machine-readable evidence docket kept under a strict covenant: one row per catch, filed in the same working session, never deleted; a catch later shown false is amended in place with the proof.

Summary of what userland can and cannot do (details in the first doc):

- **Works:** a pre-commit hook demanding an independent external model's `VERDICT: CLEAR` keyed to the exact staged blob sha256s; post-commit notarization of every commit into durable git notes (`refs/notes/adversary`) with the reviewer's verdict embedded; a pre-push guard that refuses un-evidenced history and ships the notes ref automatically; a self-contained history auditor vendored per-repo; CI re-audit with `enforce_admins` branch protection. Across ~68 gated commits its own reviews have now forced remediation on 18 documented catch-events aggregating **~60+ distinct defects and covenant violations**, **five separate cases of the authoring agent defending invented claims against the reviewer** (the core problem statement of this issue), plus two proofs of the gate behaving correctly under failure and under attack. The densest concentration was in the enforcement tooling's OWN code — the thing built to catch defects, made to review itself, was the most defect-riddled thing in the set. Full breakdown and the complete docket follow.
- **Cannot be closed in userland:** the agent-side bypass/forgery class. Our PreToolUse deny-guard (regex over command strings) blocks `--no-verify`, hooks-path re-pointing, plumbing, notes mutation, and writes to the gate's state files — but it is advisory-by-construction and fails open on anything it cannot parse. Only the harness can make the commit tool-call itself conditional on a reviewer verdict, which is exactly what this issue requests.

The full suite (hooks, installer, auditor, guard, selftests) is MIT and public: [`adversary-gate` plugin on the Nexusmill marketplace](https://github.com/Nexusmill/colibri-marketplace/tree/main/plugins/adversary-gate).

---

## The evidence, refreshed (2026-09-01)

**Commit-to-defect ratio.** Since arming on 2026-08-30, the gate has notarized **~68 code-bearing commits** across nine repos (Nexusmill 28, Tools 18, colibri-code-review 12, colibri-marketplace 4, repo-memory 3, three others 1 each). Its evidence docket holds **18 catch-events** that forced remediation, aggregating **~60+ individual defects and covenant violations**. Framed conservatively:

- **~1 in 4 gated commits carried a real defect** the gate forced out before it could ship (16 of the 18 rows are defect catches; 2 are proofs the gate behaved correctly under failure/attack).
- **~0.9 remediated findings per gated commit** overall — though most of the 68 commits pass CLEAR clean, and the findings concentrate heavily in two places: the gate's own code (~30 findings) and a single historical audit the gate forced (~24 covenant violations surfaced at once).

The concentration is itself the point: **the enforcement tooling — the code built to catch defects — was, when made to review itself, the most defect-riddled code in the set**, carrying multiple independent *total-bypass* classes that would have silently rendered the gate a no-op.

**By class (what an unassisted author would have shipped):**

- **Total-bypass defects in the gate's own code** — merge / hook-edit / code-deletion bypasses (EV-001); a POSIX `100644` fail-open that silently disarmed the entire gate on *every* Linux/macOS clone of three already-armed repos (EV-003, CRITICAL); the forgery route — an agent writing the clearance file directly with correct hashes — identified in design review and the pivot for the harness-side layer **this issue requests** (EV-005, CRITICAL); a hardcoded git path that left the public plugin dead-on-arrival on any non-authoring machine (EV-008).
- **The author defending invented claims** (the issue's founding thesis, reproduced five times against the agent that built the gate) — twice claiming fixes a failed edit-driver had never written (EV-001 #1, EV-002 #2); once claiming a guard condition that did not exist (EV-010 #3); once a fix that silently deleted data while its author claimed "canonical data preserved on every collision" (EV-016); once calling an empty-model-chain crash "impossible" in a code comment when two reachable inputs produce it (EV-018). Each was disproved by the reviewer **against the staged bytes**, not argued down.
- **Remediations destroy data too** — a fix for a schema defect (EV-013) itself silently discarded two paid review records; the gate reviewed the *remediation* as adversarially as a feature and read the deletion out of the diff (EV-016). "Review fixes like any change" is now doctrine.
- **The covenant sweep** (EV-015) — once the gate forced the audit, ~24 violations by past sessions surfaced at once: stale tests masking evolved-stronger code, orphaned registry anchors, 13 green test batteries wired to nothing, 9 features shipped with no test at all. A fifth of the harness's verdicts had quietly stopped meaning anything.
- **The gate blocking its own promotion** (EV-018) — the commit that swapped the reviewer model drew **three BLOCKs before CLEAR**: the new model, reviewing its own promotion, caught a crash path, a dead transport-failure fallback, and two false invariant claims in the safety tool's own security comments — and the final CLEAR arrived through the new fallback path exercising itself live.
- **Proofs of correct behavior under stress** (not defects — evidence the design holds): the reviewer hung ~50 minutes and returned empty; the gate **failed closed and BLOCKed** rather than clearing an unreviewed commit (EV-004). Within an hour of registration the harness guard blocked its **own author** twice (a commit message containing a trigger word; a bare directory listing of the gate's state dir) — reworded, never weakened (EV-012). *(This very evidence update tripped that same guard once — a docket row named an internal git config token in prose — and was reworded rather than the guard relaxed. The false-positive-then-reword loop is working as designed.)*

<details>
<summary><b>Complete evidence docket (18 rows)</b></summary>

| ID | Repo | Layer | What it caught | Author disputed? |
|---|---|---|---|---|
| EV-001 | Tools | gate-review (6 rounds, gate's birth) | 6 bypass classes in the enforcement tool itself: merge exemption, hook-edit, deletion/rename-away, an empty-response crash, a dismissed BEL byte, a per-clone-arming overpromise | **False rebuttal #1** — claimed fixes never written |
| EV-002 | Tools | gate-review (7 rounds, installer) | 11 findings incl. CRLF-corrupted-shim blessing, foreign-hooks-config equivalence misjudgment, exit-contract gaps | **False rebuttal #2** — claimed a step present that wasn't |
| EV-003 | Caliper (+3 retro) | gate-review | POSIX `100644` hooks silently skipped → the whole gate a no-op on every POSIX clone of 3 armed repos | Accepted |
| EV-004 | Tools | runtime (fail-closed proof) | Reviewer hung 50 min, returned empty → gate BLOCKed instead of clearing | n/a (design proof) |
| EV-005 | all armed | advisor design review | The forgery route: an agent writing the clearance file directly bypasses layers 1/3/4 silently | Had not considered it |
| EV-006 | Tools | pre-push guard (self-caught live) | `rev-list --not` toggle re-included pre-baseline history, refused a fully-notarized push | n/a (self-caught) |
| EV-007 | 4 GitHub repos | advisor (CI design) | PR trigger checks out a synthetic merge commit that can never carry a note → every PR flagged forever | Shipped before catch |
| EV-008 | colibri-marketplace | gate-review (byte-copies of cleared code) | 3 portability defects incl. hardcoded git path → public plugin dead on arrival elsewhere | Expected a rubber stamp |
| EV-009 | Tools + 4 repos | gate-review (2 rounds) | Backwards merge-strategy security logic minting N unaudited commits; overstated status line | Argued reversed reasoning; conceded |
| EV-010 | Tools (hy4-review) | gate-review | Crash-loop retry re-adding a 400-rejected key; missing error handling | **False rebuttal #3** — claimed a guard condition that didn't exist |
| EV-011 | Nexusmill | gate-review | Duplicate object key-pair in a manifest; "validates" was true for the wrong property | Claimed validation passed |
| EV-012 | machine-wide | harness guard (live) | Blocked its own author twice within the hour (trigger word in prose; a listing of the state dir) | n/a (design proof) |
| EV-013 | colibri-code-review | gate-review | Mixed-era schema drift across weeks of syncs: 15 review records fragmented/invisible | Rebutted fix location (verified correct); conceded defect |
| EV-014 | Nexusmill | auditor-mindset sweep | Structural misfiling: 3 remediation rows + 8 dockets filed into the wrong arrays → invisible to every consumer | Author's own past sessions |
| EV-015 | Nexusmill | features critic (forced by the audit) | ~24 covenant violations: stale tests hiding stronger code, orphaned anchors, 13 unwired batteries, 9 untested features | Past sessions, this agent included |
| EV-016 | colibri-code-review | gate-review (on a REMEDIATION) | The EV-013 fix itself silently deleted 2 paid review records; "13 recovered" hid that 15 existed | Claimed "preserved on every collision" — silent about the discarded side |
| EV-017 | Nexusmill | gate-review advisory (inside a CLEAR) | A truth-pass fixed one stale number and missed a second identical one three rows away | Declared complete without checking for other occurrences |
| EV-018 | Tools (the gate itself) | gate-review ×3 (2 findings BLOCKs + 1 fail-closed) | On its own model-promotion commit: an empty-chain crash, a dead transport-failure fallback, 2 false invariant claims in its own security comments | Declared the crash "impossible"; left a stale invariant claim |

Machine-readable source: `colibri-code-review/docs/gate_evidence.json` (human view `GATE_EVIDENCE_DOCKET.md`).

</details>

**Ordinary work, not just catch-days.** The two most recent commits (test-coverage batteries for a hardware-telemetry agent and an acceleration runtime) each passed **CLEAR** with the reviewer independently verifying the coverage-ratchet arithmetic, the fail-honest test construction (no vacuous passes), and no cross-contamination between checks — and, for one, confirming a subtle *honesty* reframe the author had already made rather than papering over: an app-level path-traversal guard proven to be dead defense behind Windows HTTP.sys kernel canonicalization, so the test was written to assert the real end-to-end no-leak outcome and the guard's untestability was docketed openly. Clean passes earn no docket row, but they show the independent reviewer adding value on routine changes, not only when it catches a bug.

---

<details>
<summary><b>Doc 1 — LAYERED_ENFORCEMENT.md</b> (the threat model: four layers, honest limits)</summary>

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

</details>

<details>
<summary><b>Doc 2 — GATE_ADOPTION_PLAYBOOK.md</b> (the complete adoption runbook, every failure mode field-verified)</summary>

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

</details>
