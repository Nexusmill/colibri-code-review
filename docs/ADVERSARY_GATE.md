# ADVERSARY_GATE.md - the mandatory adversarial commit gate (G39) in this repo

> Source of truth: `C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py`
> (the tool) and `.githooks/pre-commit` here (the shim). Born 2026-08-30 from the owner's
> order after plan-triangulation proved that authors - external models AND the in-session
> agent - defend invented claims: *"every bit of code written, before it's committed,
> needs an adversarial review... build it so you have no choice."* This repo is ARMED.

## What it is

A git pre-commit hook (routed via `core.hooksPath .githooks`, so it fires on EVERY commit
path - CLI git, helper scripts, IDEs) that **refuses any commit staging code** unless an
INDEPENDENT external model has issued `VERDICT: CLEAR` keyed to the exact sha256 of each
staged blob. The reviewer is never the author. Re-editing a cleared file invalidates its
clearance automatically - clearance follows bytes, not intentions.

## What counts as "staging code"

- Files with a code extension: `.py .js .json .ts .jsx .tsx .html .css .ps1 .sh .bat .c
  .cpp .h .rs .go .java .glsl .osl .mjs .cjs .mts .cts` (`.json` added 2026-08-31, owner's
  order: manifests, registries and configs are load-bearing - a forged manifest row is a code
  change; the four JS/TS module forms added 2026-09-04, EV-029: an ES-module security guard had
  passed a gate run with a clearance covering only its test file - the same set lives in the
  vendored auditor, and re-vendoring it makes the auditor demand notes for module files in
  post-baseline history, which is the fail-closed direction)
- **Anything under `.githooks/`** regardless of extension - a hook edit could neuter the
  gate itself (finding from the gate's own birth review, round 2)
- **Anything under `.github/workflows/`** - the CI audit workflow is enforcement config
  too; editing it un-gated would be the same hole (layered-enforcement review 2026-08-31)
- **Deletions of code files and renames-away** (code renamed to a non-code extension) -
  removing or hiding code is a code change (birth review, round 3); keyed as `D:<path>`
  with the removed HEAD blob's sha
- **Merges are NOT exempt** - a merge can carry un-gated commits; the staged result is
  reviewable like any other change

Docs (`.md`) and other non-code files pass free - documentation commits need no
clearance. JSON does NOT pass free since 2026-08-31: manifest/registry rows are reviewed
with the change they describe.

## The working loop

```text
1. edit + stage everything (git add <paths>)
2. python C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py run
     -> the model gets the staged diff (unified=8) + full staged files
        (250KB/file, 900KB total caps; oversized files judged from hunks)
3a. VERDICT: CLEAR  -> clearances written; commit NOW (any re-edit goes back to 2)
3b. VERDICT: BLOCK  -> findings with severity/file/line/trigger/impact.
     Fix each real finding, restage, back to 2.
     A WRONG finding is rebutted FACTUALLY:
       ... run --context "why the finding does not hold, with file/line evidence"
     The reviewer re-verifies rebuttals against the bytes and will call out a false
     rebuttal - never argue a finding away in prose outside the loop.
4. git commit    (the hook re-checks shas; passes while staged bytes are unchanged)
```

Other commands: `... check` (what the hook runs - exit 1 with a per-file
stale/unreviewed listing), `... status` (staged files vs clearance state).

## Configuration

- **Key:** `OPENROUTER_API_KEY` env - required to RUN the adversary; never printed.
- **Model:** default `tencent/hy3` (sub-cent per commit); `ADVERSARY_MODEL` env or
  `--model` overrides. 429s retry 3x with 30s backoff. An empty model response fails
  CLOSED (auto-BLOCK), never an exception.
- **State:** `.adversary/` (gitignored) - `clearance.json` (per-file sha-keyed verdicts)
  and `reviews/gate_<timestamp>.md` artifacts (model, usage, files, full verdict text).
- **Selftests:** `gate_selftest.py` (16 checks) and `install_selftest.py` (25 checks) in
  the tool folder; both run offline via `ADVERSARY_FAKE`, which is honored ONLY inside
  `advgate_*`-named selftest repos - it cannot stub the real gate (birth review, r2).

## The escape hatch is not yours

`.adversary/OVERRIDE` (a file containing a written reason) lets exactly ONE commit
through with a loud warning, then deletes itself. It exists for the OWNER's emergencies.
An agent using it is a protocol violation, full stop - equivalent to disabling the gate.

## Arming truth (per clone)

Git cannot ship config: **a fresh clone is UNARMED** until `git config core.hooksPath
.githooks` runs in that working copy. This repo's checkout is armed; verify any clone
with:

```bash
python C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py <repo> --verify-only
```

Two hardening facts learned in the field (2026-08-30, now baked into this repo's
arming): the hook must be committed with index mode **100755** - POSIX git silently
*skips* a non-executable hook, turning the mandatory gate into a no-op on any POSIX
checkout (`git update-index --chmod=+x .githooks/pre-commit`); and
`.githooks/.gitattributes` pins the shim to `eol=lf` so an `autocrlf=true` checkout can
never hand `/bin/sh` a CRLF script it refuses to parse.

## Durable notarization + the audit tripwire (2026-08-31)

The hook alone is advisory - git offers `--no-verify`, plumbing, GUI escapes, unarmed
clones, and (worst) direct forgery of `.adversary/clearance.json`. The answer is layered
(full doc: [LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md)): a `post-commit` hook runs
`adversary_gate.py record`, which writes a durable **git note** on
`refs/notes/adversary` iff every changed code blob matches a fresh CLEAR (fail-closed:
no match, no note - note ABSENCE is the tripwire signal); the vendored
`.githooks/adversary_audit.py` re-verifies every commit after
`.githooks/adversary_baseline` and screams on unnotarized or sha-mismatched history;
CI runs the same auditor on push. Owner OVERRIDEs become provenance-carrying OVERRIDE
notes - visible forever, blessing only the exact blobs they were invoked for. **Push
notes with the branch:** `git push origin refs/notes/adversary`.

## Why it exists (the receipts)

The gate's own birth review ran SIX adversarial rounds and caught: a merge bypass, an
empty-response crash, a hook-edit bypass, a deletion bypass, a dismissed-as-rendering
artifact that was a literal BEL byte, a per-clone arming overpromise - **and one false
rebuttal from the very agent building it** (round 5: a claimed fix that had never been
written; the adversary read the staged bytes). The installer's birth review (7 rounds,
11 findings, one more conceded false rebuttal) repeated the lesson the same day. Authors
defend invented claims; the gate is structural distrust of exactly that.
