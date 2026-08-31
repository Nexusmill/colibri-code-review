# EXTERNAL_SUBAGENT.md - provisioning an external subagent that can arm the gate and run reviews

> The checklist for getting everything in place so a HEADLESS agent session - another
> machine, another checkout, a scheduled job, or a launcher-spawned worker - can run
> `install_gate.py`, clear commits through the adversary gate, and drive colibri sweeps.
> Every requirement below is grounded in a hardcoded path or env read in the actual
> tools; skip one and the failure mode is listed next to it.

## The five machine prerequisites

| # | requirement | why (code fact) | failure mode if missing |
|---|---|---|---|
| 1 | **Git for Windows at `C:\Program Files\Git\cmd\git.exe`** | `adversary_gate.py` hardcodes `GIT` to that path with NO fallback | the gate tool itself dies on any command -> commits are refused (hook fail-closed) and none can clear. (`install_gate.py` and the selftests DO fall back to `git` on PATH; the gate proper does not.) |
| 2 | **Python 3.11 at `C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe`** - or ANY `python` on the hook's PATH | the shim's `PYBIN` tries the 3.11 path, then falls back to bare `python` | no python visible to `sh` -> the hook errors -> every commit refused |
| 3 | **The Tools repo at `C:\Users\User\source\repos\Tools`** | the shim's `GATE=` and every documented command hardcode the canonical path; this is the single-operator ecosystem convention (TOOLS_MANIFEST.md) | `install_gate.py` exits **3**: armed but FAIL-CLOSED - commits refused, none clearable. Clone/sync the Tools repo to that exact path BEFORE arming anything |
| 4 | **`OPENROUTER_API_KEY` in the PROCESS environment** | `adversary_gate.py run` refuses to run without it; colibri/`run_batch.py` read the same variable | gate runs impossible (checks still refuse commits); reviews return the no-key message |
| 5 | **The target repo checked out, on the right branch** | clearances and commits are per-clone; `core.hooksPath` is per-clone config | arming the wrong clone gates nothing where you meant it |

### Getting the key into the process (without it ever transiting chat)

The owner sets the key once (`setx OPENROUTER_API_KEY "sk-or-v1-..."` on Windows).
`setx` only affects NEW shells, so an already-running agent session pulls the User-scoped
value into its own process:

```powershell
$env:OPENROUTER_API_KEY = [Environment]::GetEnvironmentVariable('OPENROUTER_API_KEY','User')
```

Verify with a boolean, never by printing:
`python -c "import os;print(bool(os.getenv('OPENROUTER_API_KEY')))"` -> must print
`True`. The key is never hardcoded, echoed in full, written to a file, or committed -
and never pasted through a chat channel to "give" it to an agent; provision the machine,
not the conversation.

## Launching the headless session

A one-shot headless Claude Code worker, from the target repo:

```powershell
cd <target-repo>
claude -p "<task prompt - e.g. the arming sequence from GATE_INSTALLER.md>" `
  --allowedTools "Bash,Read,Grep,Glob"
```

- Give it the narrowest toolset the task needs; the arming sequence needs Bash (+ Read
  for verification).
- Working directory = the target repo, so relative git operations land where intended.
- For a persistent worker instead of one-shot, drive sessions with the
  session-driver pattern (launch, assign, monitor, collect) rather than fire-and-forget.

### The billing trap (verified the hard way)

If the worker is launched through an **OpenRouter-backed launcher** (a wrapper that
points Claude Code at non-Anthropic models), set the model overrides in the launcher's
environment - `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` /
`ANTHROPIC_DEFAULT_HAIKU_MODEL`. Setting only `CLAUDE_CODE_SUBAGENT_MODEL` is NOT
sufficient: subagent traffic silently billed real Anthropic models until the DEFAULT_*
overrides were added. Also: advisor-style tools that forward the transcript to a
stronger Anthropic reviewer are structurally unusable when the main model is
non-Anthropic - don't wire them into such workers.

### Permissions (first run on a machine/profile)

A fresh profile will permission-prompt on every tool family, which a headless `-p` run
cannot answer. Pre-approve in the profile's `settings.local.json`: the Bash patterns the
task needs, plus - if the worker uses the universal-tools plugin -
`mcp__universal-tools__*` rows and `Skill(<name>)` rows for any skills it loads. There is
no universal wildcard; each server/skill gets its row. Alternatively run the first
session interactively once and approve, then go headless.

## What to actually ask the worker to do

- **Arm a repo:** the exact sequence + report contract in
  [GATE_INSTALLER.md](GATE_INSTALLER.md#driving-it-with-an-external-subagent). The
  installer's exit code is the machine-readable truth: demand 0, treat 3 as "provision
  the Tools repo first", treat 1 as stop-and-report.
- **Audit a fleet:** `install_gate.py <repo> --verify-only` per repo; collect the
  ARMED / ARMED (FAIL-CLOSED) / UNARMED lines.
- **Review sweep:** `run_batch.py` per [BATCH.md](BATCH.md) / [../AGENTS.md](../AGENTS.md)
  (rank -> sweep -> verify-every-finding-before-changing-anything -> fix -> re-run).
- **Commit code:** the worker lives under the same G39 loop as anyone: stage -> gate
  `run` -> fix or factually rebut -> commit. The OVERRIDE escape is the owner's alone;
  a worker touching it is a protocol violation.

## Trust but read back

A subagent's report is a claim. After any external arming or sweep, verify from your own
session: `install_gate.py <repo> --verify-only`, `git -C <repo> log --oneline -3`, and
(for reviews) the saved artifacts in `.colibri_reviews/`. Multiple sessions work these
repos concurrently - re-read `git status` immediately before any commit or manifest
edit, and stage explicit paths, never `-A`, in a tree another session may be using.
