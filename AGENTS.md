# AGENTS.md

> **ARM THE COMMIT GATE (mandatory, once per clone):** `git config core.hooksPath .githooks` - every commit staging code then requires the adversarial clearance (tool: Nexusmill Tools repo, adversary-gate/). A fresh clone is UNARMED until this runs.

# AGENTS.md — driving Colibri from a coding agent

This note is for a coding agent (Claude, Cursor, etc.) asked to sweep a repo with Colibri.
Colibri already exists in this folder; you drive it, you don't rebuild it.

## The one secret: `OPENROUTER_API_KEY`

Colibri authenticates to OpenRouter with the environment variable `OPENROUTER_API_KEY`.
That is the **only** secret involved. Rules:

- **Never** hard-code it, print it in full, write it to a file, or commit it.
- The user sets it themselves (see INSTRUCTIONS.md). Your job is only to make sure the
  **process you launch** can see it.

### Picking up the key once the user has set it

If the user set the key with `setx` on Windows (or edited their shell rc on macOS/Linux),
an **already-open** terminal won't have it yet — `setx` and rc edits only apply to *new*
shells. So before you run a job, load the user-scoped variable into the process environment:

**Windows / PowerShell** — pull the User-scoped variable into this session, then run:

```powershell
$env:OPENROUTER_API_KEY = [Environment]::GetEnvironmentVariable('OPENROUTER_API_KEY','User')
python run_batch.py <paths> --model z-ai/glm-5.2 --effort high
```

**macOS / Linux** — a freshly-sourced shell already has it; otherwise:

```bash
export OPENROUTER_API_KEY="$(grep -m1 OPENROUTER_API_KEY ~/.zshrc | cut -d'"' -f2)"
python run_batch.py <paths> --model z-ai/glm-5.2 --effort high
```

If `python -c "import os;print(bool(os.getenv('OPENROUTER_API_KEY')))"` prints `False`,
the key isn't in the process env yet — fix that before running, don't guess.

## Running a sweep

`run_batch.py` is the headless entry point. It reads the key from the env, writes one
Markdown review per file to `--out`, and prints per-file cost + a running total.

```bash
python run_batch.py path/to/repo --model z-ai/glm-5.2 --mode bug --effort high --out reviews
```

- Pinned models: `z-ai/glm-5.2` (GLM-5.2) and `moonshotai/kimi-k3` (Kimi K3). Any OpenRouter
  id works.
- **`--max-tokens` gotcha:** reasoning tokens count against it. Keep the default `32000` for
  high-effort runs on normal files; a huge value (128k) makes high-effort reasoning run for
  many minutes per file. If a run seems hung with near-zero CPU, this is why — lower it.
- Use `--budget 0.50` to cap total spend; `--glob "*.py,*.ts"` for other languages.

## A good sweep loop

1. Rank/triage: start with the files most likely to matter (entry points, anything touching
   the network, auth, money, file I/O).
2. Run `run_batch.py` at `--effort high` on that set.
3. **Verify every finding against the source before you change anything.** Models overstate
   severity and occasionally invent bugs; confirm the exact line/behaviour first, and reject
   false positives with a reason.
4. Fix real issues, re-run, commit.

That verify-first step is the whole point — the tool surfaces candidates fast and cheaply,
but a human-or-agent check is what turns a candidate into a fix.
