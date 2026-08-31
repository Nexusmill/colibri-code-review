# GATE_INSTALLER.md - arming the gate on any repo (directly or via a subagent)

> Source of truth: `C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py`
> (selftest `install_selftest.py`, 25/25). Shipped 2026-08-30; first live arming the same
> day: `E:\AI\Caliper` (commit 63ebec8), whose adversary review immediately caught the
> 100644 exec-mode fail-open now covered below - the installer's proving sequence works.

## What `install_gate.py` does

`python C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py <repo-path>`

1. Resolves `<repo-path>` (any path inside the working copy) to the repo toplevel; a
   non-repo, or a machine without git, fails with a clean `FAIL:` line - no traceback.
2. Reads the **canonical shim** `Tools/adversary-gate/pre-commit` - the single source of
   truth, byte-identical to the shims armed in Nexusmill / Tools / colibri-code-review /
   Caliper. It is deliberately NOT embedded in the installer (one copy that cannot
   drift), sanity-checked (`#!/bin/sh` + gate reference) so a mangled canonical can't be
   propagated, and LF-normalized on read.
3. Conflict guards (each needs `--force` to override): an existing `core.hooksPath`
   pointing somewhere OTHER than `.githooks` (equivalent spellings - `./.githooks/`,
   absolute, backslashes - are recognized as already-ours, not foreign); an existing
   `.githooks/pre-commit` with DIFFERENT content. A shim that is canonical except for
   CRLF endings is repaired without `--force` (the content is ours; only the endings are
   broken).
4. Warnings (install proceeds; the operator must know): real hooks in the default
   `.git/hooks` dir that `core.hooksPath` will BYPASS; a `package.json` mentioning
   husky / simple-git-hooks / lefthook / core.hooksPath - an npm-managed hook setup can
   silently re-point `core.hooksPath` on `npm install` and DISARM the gate (re-audit
   with `--verify-only` after any npm install in such repos).
5. Installs: writes the shim bytes to `.githooks/pre-commit` (fsync + byte-verified
   readback), `chmod 0o755`, appends `pre-commit text eol=lf` to
   `.githooks/.gitattributes` (durable LF even under `autocrlf=true`) and `.adversary/`
   to the repo's `.gitignore` (transient gate state never gets committed) - both
   idempotent - then sets `git config core.hooksPath .githooks` and re-reads everything
   to verify, including that the gate tool the SHIM execs actually exists on this
   machine.

### Exit codes (automation keys on these)

| exit | meaning |
|---|---|
| 0 | armed AND functional (shim canonical, hooksPath set, gate tool present) |
| 3 | armed but **FAIL-CLOSED**: the Tools repo is not at the shim's canonical path on this machine - every commit will be refused and NONE can clear. A lockout, not a working gate ([EXTERNAL_SUBAGENT.md](EXTERNAL_SUBAGENT.md) has the prerequisites) |
| 1 | anything else: not a repo, conflict without `--force`, verification failed, unarmed (verify-only) |

### Audit mode

`... install_gate.py <repo> --verify-only` changes nothing and reports
`ARMED` / `ARMED (FAIL-CLOSED - gate tool missing)` / `UNARMED` plus three detail lines:
`core.hooksPath`, shim state (`canonical` / `crlf (...)` / `different` / `absent` - a
CRLF-corrupted shim is NEVER blessed as armed, since `/bin/sh` rejects it), and gate-tool
presence.

## The arming commit - the proof IS the procedure

The installer never commits (staging is the driver's job, and mixing into a dirty index
is not its call). The commit that lands `.githooks/` is itself gated - which is exactly
what proves the hook fires in this clone, free of charge:

```bash
git add .githooks/pre-commit .githooks/.gitattributes .gitignore
git update-index --chmod=+x .githooks/pre-commit
#   ^ REQUIRED: os.chmod cannot set an exec bit on Windows, and POSIX git silently
#     SKIPS a 100644 hook - the index mode is what clones inherit
git commit -m "chore(gate): arm the mandatory adversarial commit gate (G39)"
#   -> EXPECT: "ADVERSARY GATE: commit REFUSED" listing the staged .githooks files.
#      That refusal is the end-to-end verification. If the commit SUCCEEDS here,
#      something is wrong - stop and audit with --verify-only.
python C:\Users\User\source\repos\Tools\adversary-gate\adversary_gate.py run \
  --context "arming commit: canonical shim, installed by install_gate.py"
git commit -m "chore(gate): arm the mandatory adversarial commit gate (G39)"
#   -> passes while the staged bytes stay identical
```

Finish all edits BEFORE running the adversary: clearances are keyed to staged blob shas,
so any re-edit (or re-staging different bytes) invalidates them by design.

## Driving it with a LOCAL subagent

Any in-session subagent with Bash access can do the whole sequence. A prompt that has
worked:

> Arm the adversarial commit gate on `<repo>`. Run
> `python C:\Users\User\source\repos\Tools\adversary-gate\install_gate.py <repo>` and
> require exit 0. Then in `<repo>`: stage `.githooks/pre-commit`,
> `.githooks/.gitattributes` and `.gitignore`; run
> `git update-index --chmod=+x .githooks/pre-commit`; attempt the commit and CONFIRM it
> is refused with "ADVERSARY GATE"; run the gate's `run` command (needs
> OPENROUTER_API_KEY in your environment); commit. Report: installer exit code, the
> refusal line, the verdict line, and the final commit hash. If any step deviates, STOP
> and report - do not improvise around the gate.

Verify the subagent's report yourself with `--verify-only` and `git log -1` - reports
are claims, the readback is the fact.

## Driving it with an EXTERNAL subagent

Same sequence, executed by a headless session (another machine, a scheduled job, a
different checkout). Everything it needs on ITS machine - git, Python, the Tools repo at
the canonical path, the OpenRouter key, and the launcher recipe with its billing
pitfalls - is specified in [EXTERNAL_SUBAGENT.md](EXTERNAL_SUBAGENT.md). The short
version: without the Tools repo at `C:\Users\User\source\repos\Tools`, the arming is
fail-closed by design (exit 3) - commits refused, none clearable - so provision the
machine FIRST, then arm.

## Un-arming (owner's decision, audited)

`git config --unset core.hooksPath` in the clone. The shim's own banner calls this an
audited decision; an agent doing it to get past the gate is a G39 violation, same as
using `.adversary/OVERRIDE` without the owner's say-so.
