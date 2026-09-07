# CODEX_GATE_IMPLEMENTATION.md - the G39 adversarial commit gate on Codex, step by step

> **Doc version: 1.1 - 2026-09-07.** New at 1.0; 1.1 adds section 3.5 (partial commits and how to
> commit a dispatcher edit) after the EV-043 self-check fix. Registered in [DOCS_VERSIONS.md](DOCS_VERSIONS.md).
> Audience: a Codex session (OpenAI Codex CLI / app) that must operate under the same G39
> adversarial commit gate as Claude Code and Cowork. Everything here is grounded in real
> files: `Tools/adversary-gate/codex_guard.py`, `harness_guard.py`, `hooks/`,
> `install_gate.py`; `~/.codex/config.toml`; the plugin at
> `C:\Users\User\plugins\codex-enforcement-hooks`. Companions: [ADVERSARY_GATE.md](ADVERSARY_GATE.md),
> [HARNESS_GUARD.md](HARNESS_GUARD.md), [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md),
> [LAYERED_ENFORCEMENT.md](LAYERED_ENFORCEMENT.md).

---

## Part 1 - What Codex must honor, and why

The gate is a single machine-wide policy shared by every harness (Claude Code, Cowork,
Codex). It has two agent-facing halves, and Codex must run **both**:

1. **The commit wall (git-side).** A `pre-commit` hook refuses any commit staging code
   unless an independent external model has issued `VERDICT: CLEAR` keyed to the exact
   staged blob sha256s; a `post-commit` hook notarizes the commit into a durable git note;
   a `pre-push` hook refuses un-notarized history. On the owner's machine this is armed
   **machine-wide** by git's global `core.hooksPath` (see [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md)),
   so it already fires for Codex commits in any repo, including Codex-managed worktrees under
   `$CODEX_HOME/worktrees`. Codex needs no per-session setup for the wall; it needs to
   *respect* it: run `adversary_gate.py run`, obtain CLEAR, then commit.
2. **The harness deny-guard (agent-side).** A PreToolUse hook that denies the commands an
   agent could use to get *around* the wall (`--no-verify`, hooks-path re-pointing, plumbing,
   forging the gate's state files). Claude Code registers `harness_guard.py` directly; Codex
   registers it through the **`codex-enforcement-hooks` plugin**, whose adapter
   `codex_guard.py` normalizes a Codex tool event and calls the **same** `harness_guard.decide()`.

The one rule that makes the second half trustworthy: **Codex must run the Tools originals,
never a private copy.** See Part 2.4 - this is the exact failure this integration was
rebuilt to close.

---

## Part 2 - The pieces

### 2.1 The plugin `codex-enforcement-hooks`

- Source: `C:\Users\User\plugins\codex-enforcement-hooks` (a personal-marketplace plugin,
  `.codex-plugin/plugin.json`, current version `0.2.0`).
- Installed/cached copy that Codex actually executes:
  `%CODEX_HOME%\plugins\cache\personal\codex-enforcement-hooks\<version>\`.
- Enabled in `~/.codex/config.toml`:
  `[plugins."codex-enforcement-hooks@personal"] enabled = true`.

### 2.2 `hooks.json` - the event wiring

The plugin's `hooks.json` wires three Codex native events. Every command is the **absolute
interpreter path** followed by the **Tools original** (never a bundled copy):

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": ".*", "hooks": [
        { "type": "command", "command": "C:/Users/User/AppData/Local/Programs/Python/Python311/python.exe C:/Users/User/source/repos/Tools/adversary-gate/codex_guard.py" },
        { "type": "command", "command": "C:/Users/User/AppData/Local/Programs/Python/Python311/python.exe C:/Users/User/source/repos/Tools/skill-gate/skill_gate.py pre" }
      ] }
    ],
    "PostToolUse": [
      { "matcher": ".*", "hooks": [
        { "type": "command", "command": "C:/Users/User/AppData/Local/Programs/Python/Python311/python.exe C:/Users/User/source/repos/Tools/skill-gate/skill_gate.py post" }
      ] }
    ],
    "Stop": [
      { "hooks": [
        { "type": "command", "command": "C:/Users/User/AppData/Local/Programs/Python/Python311/python.exe C:/Users/User/source/repos/Tools/skill-gate/skill_gate.py stop" }
      ] }
    ]
  }
}
```

- **PreToolUse** runs `codex_guard.py` (the G39 deny-guard) and then `skill_gate.py pre`
  (the G38 skill gate).
- **PostToolUse / Stop** run the skill gate's `post` / `stop` phases.
- Use the **absolute interpreter path**, never bare `python`: a bare interpreter that is not
  on the hook's PATH bricks the hook (see the skill-gate README's `-I -c` bootstrap note for
  the Claude side; on Codex the absolute path is the fix).

### 2.3 `codex_guard.py` - the adapter (the contract)

`codex_guard.py` reads **all** of stdin as one JSON event, `normalize()`s it into the shape
`harness_guard.decide()` expects, calls `decide()`, and maps the result to an exit code:
**0 = allow, 2 = deny.** Its normalize contract, every clause of which exists because a real
Codex payload shape defeated an earlier version (the gate caught each, rounds 1-7 of commit B):

- The tool name comes from `tool_name` | `tool` | `name`; the argument bag from `tool_input`
  | `input`, plus top-level `path` / `command`.
- A **string** argument bag is treated as the command itself.
- An **argv-array** `command` (Codex shell tools send lists) is joined into one line.
- Tool names are aliased to the canonical set: `write`->`Write`, `edit`->`Edit`,
  `multiedit`->`MultiEdit`, `bash`/`shell`->`Bash`, `notebookedit`->`NotebookEdit`.
- **Deny-on-doubt for any unrecognised shape.** If the tool name is not in the known set, OR
  the bag for a known tool carries none of the keys the guard reads with a **non-blank string
  value** (`command` for Bash; `file_path`/`notebook_path` for a file tool), the *entire* bag
  is serialized to JSON and inspected as a Bash command line. So a bypass flag, a `.adversary`
  path, or the dispatcher dir anywhere inside an exotic payload still denies; a benign tool
  (a web search) carries none and passes.
- **Fail-open on adapter/infrastructure errors only.** A parse/import/runtime error returns 0
  (availability - a hook crash must not brick the session) and writes a diagnostic to
  `last_failure.json` under `%TEMP%\codex_guard` (or `CODEX_GUARD_DIAGNOSTICS`). That file is
  never adversary clearance; a recorded failure means the action was *allowed without review*
  and must get an explicit audit pass during verification. Explicit policy **denials** are
  always preserved - fail-open covers the reader, never a deny-worthy event.

### 2.4 The single-source rule (why this was rebuilt)

**Codex must execute the Tools originals, not a copy.** An earlier Codex integration shipped
**copies** of `harness_guard.py`, `codex_guard.py`, and `skill_gate.py` under the plugin's
`scripts/` directory and ran those. That is exactly how a guard drifts: the plugin's private
`harness_guard.py` (and its `decide()`) could diverge from the canonical one that Claude Code
runs, so the two harnesses would enforce different policies, and a change to the canonical
guard would silently not reach Codex.

The rebuild (2026-09-06) deleted the `scripts/` copies and re-pointed `hooks.json` at the
Tools originals; `codex_guard.py` imports `harness_guard` from its own (Tools) directory, so
there is exactly one `decide()`. The Codex adapter selftest now statically checks that the
plugin's `hooks.json` - the source **and every cached install version** under
`$CODEX_HOME/plugins/cache` - runs the Tools paths with the absolute interpreter and contains
no `/plugins/` script reference. **Never recreate the `scripts/` copies.**

### 2.5 Codex worktrees and the `.codex` setup script

Codex creates real `git worktree add` worktrees under `$CODEX_HOME\worktrees`, detached at
the chosen branch's HEAD, when a chat starts. Because arming is machine-wide (global
`core.hooksPath`), those worktrees are armed for the **commit wall** automatically - the
absolute dispatcher dir resolves in a detached worktree just as in the main checkout.

To make an unarmed or misconfigured worktree fail loudly at setup, the per-project Codex
**environment setup script** (stored under the project's `.codex/` folder) should run:

```
python C:/Users/User/source/repos/Tools/adversary-gate/install_gate.py . --verify-only
```

The exact on-disk format of the `.codex` setup file is not publicly documented and no
generated example existed to copy; the owner generates it once through the Codex app
(Settings -> local environment) and commits it, after which `arm_repo.py --codex-env <file>`
can copy it into newly armed repos. Arming does **not** depend on this file - the global
dispatcher already arms Codex worktrees; the setup script only surfaces a broken state early.

---

## Part 3 - Step by step: install, verify, operate

### 3.1 Install / re-point the plugin (one-time, or after any plugin edit)

1. Edit only the plugin **source** at `C:\Users\User\plugins\codex-enforcement-hooks`
   (`hooks.json`, `.codex-plugin/plugin.json`); bump the `plugin.json` `version` on any
   change (Codex runs from the versioned cache, not the source).
2. Reinstall so Codex picks it up:
   ```
   codex plugin add codex-enforcement-hooks@personal
   ```
   Codex installs into `%CODEX_HOME%\plugins\cache\personal\codex-enforcement-hooks\<version>\`
   and reports the installed root. Open a new thread to load the refreshed hooks.
3. Confirm the source and every cached version point at Tools with the absolute interpreter:
   ```
   python C:/Users/User/source/repos/Tools/adversary-gate/codex_guard_selftest.py
   ```
   Expect `codex_guard_selftest: N/N` and the line
   `plugin hooks point at Tools with the absolute interpreter: True` for the source and each
   cache entry.

### 3.2 Verify the deny-guard actually denies

Feed the adapter a few events by hand (this is what the plugin does per tool call):

```
echo {"tool":"bash","command":"git status"}                | python C:/Users/User/source/repos/Tools/adversary-gate/codex_guard.py ; echo rc=$?   # -> 0 (allow)
echo {"tool":"bash","command":"git commit -n -m x"}         | python C:/Users/User/source/repos/Tools/adversary-gate/codex_guard.py ; echo rc=$?   # -> 2 (deny: -n)
echo {"tool":"write","input":{"target":"...clearance file..."}} | python .../codex_guard.py ; echo rc=$?   # -> 2 (deny: state dir, via deny-on-doubt)
```

(Do not spell the gate's state-dir path on a live shell line - the guard denies that too;
the adapter selftest exercises it in a temp dir.)

### 3.3 Operate under the commit wall (the loop Codex lives in)

Identical to every other harness (see [ADVERSARY_GATE.md](ADVERSARY_GATE.md) and the
[GATE_ADOPTION_PLAYBOOK.md](GATE_ADOPTION_PLAYBOOK.md)):

1. **Finish all edits, then stage EXPLICIT paths.** `git add <paths>` - never `-A`, and note
   that a bare `git commit` afterwards commits the **whole index**, not only what you added.
   In a repo another session may be using, verify `git diff --cached --name-only` shows only
   your paths before committing, or use `git commit -- <paths>`. (This exact trap bundled a
   concurrent session's staged work into a re-vendor commit on 2026-09-06.)
2. **Run the adversary:** `python C:/Users/User/source/repos/Tools/adversary-gate/adversary_gate.py run --context "<intent>"` (needs `OPENROUTER_API_KEY`). Front-load the verbatim
   `git diff --cached --name-only` into `--context` so the reviewer sees exactly the staged
   set - a mismatch between your stated scope and the staged set is itself a finding.
3. **On BLOCK:** fix each real finding and restage, or rebut a wrong one factually with
   `--context`. **A BLOCK is a stop** - never commit on an older/stale clearance that a
   different staged set happened to match.
4. **On CLEAR:** commit immediately; the post-commit hook notarizes it. Push normally; the
   pre-push guard audits and ships the notes ref.
5. Never touch `.adversary/OVERRIDE` (owner-only) or `--no-verify`.

### 3.4 Prove a worktree / the machine

```
python C:/Users/User/source/repos/Tools/adversary-gate/install_gate.py . --verify-only   # this checkout
python C:/Users/User/source/repos/Tools/adversary-gate/install_gate.py --census          # everything
```

`--verify-only` prints the epoch state and a `dispatchers`/`DANGLING`/`STALE`/`TAMPERED` line;
`--census` lists every checkout and worktree (see [UNIVERSAL_ARMING.md](UNIVERSAL_ARMING.md)).

---

### 3.5 Committing: partial commits, and editing a dispatcher (EV-043, 2026-09-07)

Two facts about the commit wall that bit the author and will bite Codex:

- **Partial commits work, but there is history here.** `git commit -- <path>` (a *partial* commit)
  makes git build a temporary index and hand the hook an ABSOLUTE `GIT_INDEX_FILE`. Before Tools
  `7ba0e3b` the machine-wide dispatcher's self-check inherited that variable, read the *committing*
  repo's temp index instead of the suite's, and refused every partial commit from an armed repo
  with a misleading `dispatcher hooks/pre-commit is MODIFIED ... failing CLOSED` - on a byte-clean
  dispatcher. The fix runs every suite-side git in a CLEAN git context (a `suite_git` helper with
  all `GIT_*` context variables unset), so `git commit -- <paths>` is fine now from any armed repo.
  If you see that message on a clone whose dispatcher you did not touch, the clone predates the
  fix: re-vendor it (`install_gate.py <repo>`), or use a plain `git commit` after verifying
  `git diff --cached --name-only` shows only your paths (a plain commit leaks only a relative
  index and always worked).

- **You cannot commit a dispatcher edit *through* the dispatcher.** The self-check is strictly
  fail-closed: whenever `hooks/pre-commit` (or `post-commit` / `pre-push`) differs from its
  committed blob or is untracked, it refuses to run - there is NO in-band exception (one was tried
  and leaked a hole in three straight review rounds, so it was removed). To change a dispatcher,
  commit through the repo's `.githooks` shim, which execs the gate with no self-check: point the
  repo's `core.hooksPath` at `.githooks`, stage the edit, run `adversary_gate.py run` for a CLEAR,
  `git commit`, then re-pin with `install_gate.py <repo>`. This is exactly how the EV-043 fix
  itself landed. Full record: `gate_evidence.json` EV-043.

## Part 4 - The `decide()` function: what it does, and its audit

`decide(tool_name, tool_input) -> None | reason` in `harness_guard.py` is the whole policy.
`codex_guard.py` and the Claude Code hook are thin wrappers around it. **Codex did not alter
the canonical `decide()`** - its git history is authored entirely under the owner's identity,
and the only "codex" mention is the 2026-09-06 rebuild commit. Codex's earlier alteration
lived in the plugin's private `scripts/harness_guard.py` copy, which is deleted (Part 2.4);
the live `decide()` is the canonical one, audited below.

### 4.1 File-tool branch (Write / Edit / MultiEdit / NotebookEdit)

The path is lower-cased and slash-normalized; a leading drive letter is dropped; each segment
is stripped of its trailing dot/space run (Windows trims those). Segments are classified:

- exact `""` or `.` = CURRENT (skip), exact `..` = PARENT (pop) - unambiguous;
- any *other* all-dot/space segment (`...`, `.. `, `. .`) = AMBIGUOUS: platforms disagree
  whether it is a parent, the current dir, or a literal name.

The guard **enumerates every reading** over the ambiguous segments (capped at 8; more than 8
is refused outright), resolves each reading's `.`/`..`, and denies if **any** reading:

- has a segment ending `~\d+` (an 8.3 short-name alias that would hide a protected name),
- contains a `.adversary` segment (clearance/OVERRIDE forgery),
- contains a `skill_gate` segment (skill-gate ledger/OVERRIDE),
- has `.git` immediately followed by `hooks` (the live hook dir), or
- has `adversary-gate` immediately followed by `hooks` (the machine-wide dispatcher dir).

`Read` is never a file tool here and is never refused.

### 4.2 Bash branch

The command is split into segments on `; & | newline`. Each rule is checked **per segment**,
so an exempt gate invocation in one segment cannot excuse a forbidden action in another. Each
segment is checked in **two views**: the raw text, and the text with every quote character
removed - the shell strips quote pairs and reassembles a token split by them
(`adversary-gate/"hooks"`, `core.hooks"Path=`), so a protected literal is judged the way the
shell sees it. Deny if **either** view trips a rule.

The rules, grouped:

- **Commit-bypass:** `--no-verify` anywhere; a shell-variable assignment of `-n`/`--no-verify`;
  `set -- -n`; a `git commit` short-flag bundle whose `n` is not preceded by a value-taking
  option (`-nm` denies, `-mn` = `-m "n"` allows); a variable-built `$VAR commit -n`.
- **Hooks-path / arming (2026-09-06):** any `--global`/`--system`/`--worktree`,
  `--remove-section`/`--rename-section`, `--edit`/`-e`, `--file`/`-f`, `include.path`/
  `includeIf` git-config write (all can re-point or drop the hooks path without naming it);
  any `GIT_CONFIG_{GLOBAL,SYSTEM,NOSYSTEM,PARAMETERS,COUNT,KEY_n,VALUE_n}` env var; and any
  `hooksPath` set to anything **except** the two arming values - the vendored `.githooks`
  (optional trailing slash) or the absolute canonical dispatcher dir - where a trailing tab,
  NBSP, quote-then-anything, or spaced `=` all deny (each reaches git as a hookless value).
- **The protected directories (no read exemption, EV-022):** any Bash reference to the
  machine-wide dispatcher dir (`adversary-gate/.../hooks`, deny-on-doubt across intermediates
  and trailing dot/space runs); an 8.3 alias (`NAME~1/.../hooks`); any literal `.adversary`;
  any `skill_gate/`; any spelling of the live `.git/.../hooks` dir. The dispatcher rule has
  **one** exemption: a segment that is, in its entirety, the arming command
  (`git config core.hooksPath <canonical>`) or the inline `git -c core.hooksPath=<canonical>
  commit ...` form - whose tail admits no `$`, backtick, `<`, or `>` so a substitution or a
  redirection cannot ride inside it.
- **Plumbing / notes:** `commit-tree`, `update-ref`, `fast-import`, `git replace`; mutating
  `git notes` subcommands; `ADVERSARY_FAKE` outside `*_selftest.py`.

`main()` fails **open** on any exception (a guard crash must never brick the harness); the
commit wall and the audit tripwire stand behind it.

### 4.3 Audit verdict: sound, with documented residuals - no code change made

I examined `decide()` in full. It is correct as written and has survived ~10 adversarial gate
rounds this cycle. I made **no change**, because the remaining gaps are the structural limits
of a text guard, and the project's own doctrine (EV-022) proves that "fixing" them adds false
confidence rather than safety:

1. **Ancestor deletion is not caught.** `rm -r .../Tools/adversary-gate` (or its 8.3 alias
   `.../Tools/ADVERS~1`, or `rm -r .../Tools`) deletes the dispatchers *and* the gate tool,
   which would disarm every repo pinned to that dir. No rule catches it, because the gate is
   also *invoked* by that same path constantly
   (`python .../adversary-gate/adversary_gate.py run`), and EV-022 is precisely the finding
   that a text guard cannot reliably tell "delete this path" from "invoke a tool at this path"
   once shadowing / PATH / aliases are in play. A rule that denied every `adversary-gate`
   reference would break the gate's own invocation; a rule that tried to exempt "invocations"
   reopens the shadowing hole. This is **detection, not prevention**: a deleted gate leaves
   later commits un-notarized, which the audit tripwire and CI flag, and the owner notices the
   tooling gone. Consistent with the layered honest claim.
2. **Symlink / glob / string-concat spellings** that never render the protected literal in the
   command or path text (e.g. a Write to a symlink whose target is the dispatcher dir) are the
   same "never spells the literal" residual. Backstopped at run time by the dispatcher
   self-check (an edited dispatcher fails closed) and after the fact by the audit tripwire.
3. **Unbounded shell indirection** (arrays, `${x:--n}`, computed values) can smuggle a bypass
   flag past the regex. Backstopped by the tripwire.
4. **Accepted deny-on-doubt false positives:** a command that merely *quotes* a guarded string
   is refused (`echo "the hooksPath var"`), as is a benign `NAME~1` filename and a read of a
   `GIT_CONFIG_*` env var. The documented workaround is to put such text in a file and run the
   file by path.

If any of these must be closed, the correct place is a **later layer** (the notary, the
auditor, CI), not more regex - which is exactly how the design already treats them.

---

## Part 5 - Maintenance rules for Codex

- **One source of truth.** Edit `harness_guard.py` / `codex_guard.py` / the dispatchers in
  `Tools/adversary-gate/` only; never in a plugin copy. After any edit, re-run
  `codex plugin add codex-enforcement-hooks@personal` and `codex_guard_selftest.py`.
- **Every rule lands RED-first with a selftest row** (`guard_selftest.py` / `codex_guard_selftest.py`),
  and the change is committed through the gate like any code.
- **Keep `~/.codex/MEMORY.md` current** so a new Codex chat does not rebuild the copies:
  record the canonical paths, that the plugin runs the Tools originals, and the single-source
  rule.
- **When the vendored auditor changes**, re-vendor every armed repo (see UNIVERSAL_ARMING.md);
  a superseded clearance is abandoned, not reused.
- **Respect the skill gate too.** The PreToolUse/PostToolUse/Stop `skill_gate.py` rows are the
  G38 half; see `Tools/skill-gate/README.md` and the skill-gate filing draft.
