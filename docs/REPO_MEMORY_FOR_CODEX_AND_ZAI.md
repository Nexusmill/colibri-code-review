# REPO_MEMORY_FOR_CODEX_AND_ZAI.md - using and wiring repo-memory in Codex and ZCode (z.ai/GLM)

> **Doc version: 1.0 - 2026-09-07.** New. How the two non-Anthropic-native harnesses - OpenAI
> **Codex** and **ZCode** (Claude Code running on the z.ai coding plan, GLM-5.3) - consume and
> install `repo-memory`, the per-repo semantic memory server. Source of truth for the server
> itself: `C:\Users\User\source\repos\repo-memory\README.md` and the `repo_memory/` package
> (`server.py`, `bootstrap.py`, `indexer.py`, `autoindex.py`, `store.py`, `colibri.py`). This doc
> only covers the two client harnesses; it does not restate the server internals.

---

## Part 0 - What repo-memory is (read this once, it is the same for both harnesses)

`repo-memory` gives **each repository its own knowledge base**. A search in Nexusmill cannot
surface a 3DPrinting row, because they are different LanceDB databases on disk. It is delivered
as a **stdio MCP server**, one instance per repo, and MCP is **client-side and model-agnostic** -
the server neither knows nor cares whether the agent behind the client is Claude, GPT/Codex, or
GLM. That single fact is why the same server works, unchanged, in Claude Code, Codex, and ZCode.

Per repo you get **four tools**, each prefixed with the repo's slug so several stores can be
loaded at once without ambiguity:

| Tool | Purpose |
| --- | --- |
| `<slug>_memory_search` | Semantic search over that repo's knowledge (the query path) |
| `<slug>_memory_recent` | Most recently dated entries |
| `<slug>_memory_write` | Persist a durable learning (survives the session) |
| `<slug>_memory_stats` | Row count, DB path, categories, and which writers contributed |

The slug comes from the server's `REPO_MEMORY_NAME` (e.g. `Nexusmill` -> tools
`nexusmill_memory_search`, ...). Storage is LanceDB under `E:\repo-memory\<slug>\` (override the
root with `REPO_MEMORY_ROOT`). Embeddings are `all-MiniLM-L6-v2`, 384-dim, **local, CPU, no API
key**; the first server start downloads the model (~a few seconds to a minute), every start after
is cached and offline.

**Indexing is automatic.** The server fingerprints every source file (size + mtime) and re-chunks
only what changed - on start, and on reads at most once per minute. Edit a doc, and the next query
already reflects it; delete one and its rows go away. There is no manual refresh to forget. (Knobs:
`REPO_MEMORY_AUTOINDEX=0` disables it; `REPO_MEMORY_AUTOINDEX_INTERVAL` seconds throttles the read
path.)

---

## Part 1 - How to USE it (identical in both harnesses, once the tools are loaded)

The tools appear to the model like any other MCP tools. The discipline is what makes them useful:

1. **Query before you work, not after you're stuck.** Before editing a file or answering a
   "why is it like this?" question, call `<slug>_memory_search` with the concept in plain words
   ("known problems in the accel worker", "why is Asset Forge sold separately", "how does the
   commit gate handle partial commits"). Colibri reviews, design decisions, and prior fixes are
   in there under sources like `docs/<file>/section` and `colibri/<mode>/findings`.
2. **Trust the segmentation.** A result is always from *this* repo's store (the result header
   names the repo). You never have to worry a hit is from another project.
3. **Write durable learnings the moment they happen**, with `<slug>_memory_write`. Good rows are
   a single fact or decision a future session would otherwise re-derive: "accel cupy->torch
   fallback is deliberate, never re-flag", "Superhive forbids selling textures". Do **not** write
   session chatter, TODOs, or anything the repo's own docs/git already record.
4. **Use `_recent` to re-orient** at the start of a task ("what changed here lately?") and
   `_stats` to sanity-check you're pointed at the right store (it prints the DB path and row
   count).

Writes land under a source that names the writer (e.g. `agents/claude-mcp`, and Codex/ZCode
writes are tagged the same way by the server), and re-seeding the markdown never touches them -
only the `docs/...` and `colibri/...` sources are purged-and-re-added on a doc change.

---

## Part 2 - Implement it for Codex

Codex reads MCP servers from **`~/.codex/config.toml`** under `[mcp_servers.<name>]` tables -
there is no per-project `.mcp.json` in Codex. This has one consequence to design around:

> **Codex MCP servers are GLOBAL.** Every server you add is loaded in every Codex session,
> exactly like repo-memory's Desktop **Chat** tab. The *data* stays segmented (each server is its
> own database), but the *tool list* is not - so you rely on the slug-prefixed tool names to pick
> the right store. Add only the repos you actually work in from Codex.

### 2.1 Add one repo's memory server

Append a block per repo to `~/.codex/config.toml`. Codex wants the env as a **subtable**
(`[mcp_servers.<name>.env]`), mirroring the existing `node_repl` entry:

```toml
[mcp_servers.nexusmill-memory]
command = 'C:\Users\User\source\repos\repo-memory\.venv\Scripts\python.exe'
args = ['-B', '-m', 'repo_memory.server']
startup_timeout_sec = 120

[mcp_servers.nexusmill-memory.env]
PYTHONPATH = 'C:\Users\User\source\repos\repo-memory'
REPO_MEMORY_DB = 'E:\repo-memory\nexusmill'
REPO_MEMORY_NAME = 'Nexusmill'
REPO_MEMORY_REPO_ROOT = 'C:\Users\User\source\repos\Nexusmill'
```

- `command` / `args` launch the server module out of repo-memory's own venv (its dependencies -
  torch/sentence-transformers/lancedb - live there, not on the system python).
- The **four env vars are the whole contract**: `PYTHONPATH` (so `repo_memory` imports),
  `REPO_MEMORY_DB` (the LanceDB directory - keep it under `E:\repo-memory\<slug>` to match the
  registry), `REPO_MEMORY_NAME` (sets the tool prefix and the result headers), and
  `REPO_MEMORY_REPO_ROOT` (the working tree it indexes markdown from).
- `startup_timeout_sec = 120` is not optional on a cold machine: the **first** start loads the
  embedding model, and Codex will kill a server that doesn't answer `initialize` in time. 120 s
  is safe; later starts are ~10 ms.
- The name (`nexusmill-memory`) is just the server id in Codex; the *tool* prefix comes from
  `REPO_MEMORY_NAME`. Keep them parallel to stay sane.

The fastest way to get the exact values for a repo is to let the bootstrap compute them once
(Part 4) and copy the four env values out of the `.mcp.json` it writes - they are identical.

### 2.2 Verify

Restart Codex, then in a session confirm the tools are present and answer:

- The `nexusmill_memory_stats` tool should exist and return a DB path + a non-zero row count.
- `nexusmill_memory_search` on a term you know is in the repo's docs should return a chunk whose
  header names the repo.

If the tools never appear: check `startup_timeout_sec` (raise it), that the venv python path is
right, and that `E:\repo-memory` is reachable (it is on the E: drive - an external/second disk).

---

## Part 3 - Implement it for ZCode (z.ai / GLM-5.3)

**ZCode is Claude Code family, but its MCP surface is a user-scope PLUGIN, not a repo file.**
ZCode runs the Claude Code agent loop on the z.ai coding plan (`builtin:zai-coding-plan/GLM-5.3`),
rooted at **`~/.zcode/cli/`**. Because MCP is model-agnostic, repo-memory needs no GLM-specific
work - the same server, the same four tools, the same data. What differs from Claude Code CLI is
*where the server is registered*. Verified on disk (this machine), MCP servers reach ZCode through
a **plugin's own `.mcp.json`**, registered **user-scope** so it loads in every session and every
repo:

- `~/.zcode/cli/plugins/cache/<marketplace>/<plugin>/<ver>/.mcp.json` carries an `mcpServers`
  block (the Claude Code plugin format). The universal-tools plugin is mounted exactly this way.
- `~/.zcode/cli/plugins/installed_plugins.json` records the plugin with `"scope": "user"`, and
  `~/.zcode/cli/config.json` enables it under `plugins.enabledPlugins`.
- `~/.zcode/cli/config.json` has **no `mcpServers` key**, and ZCode does **not** consume a
  per-repo `.mcp.json`. The repo-root `.mcp.json` the bootstrap writes (Part 4) is read by
  **Claude Code CLI / Cowork**, NOT by ZCode - do not expect arming a repo to arm ZCode.

The practical consequence mirrors Codex: **ZCode's MCP scope is GLOBAL.** Every server a
user-scope plugin declares loads in every ZCode session; the *data* stays segmented (separate
databases), and the slug-prefixed tool names pick the right store. Add only the repos you actually
work in from ZCode.

### 3.1 Add repo-memory to ZCode's plugin surface

Put the server entries in a user-scope plugin's `.mcp.json` `mcpServers` block. The entry shape is
the Claude Code plugin shape - the same block the bootstrap writes for Claude Code, including the
four `env` vars (the `type` field is optional here):

```json
{
  "mcpServers": {
    "nexusmill-memory": {
      "command": "C:/Users/User/source/repos/repo-memory/.venv/Scripts/python.exe",
      "args": ["-B", "-m", "repo_memory.server"],
      "env": {
        "PYTHONPATH": "C:/Users/User/source/repos/repo-memory",
        "REPO_MEMORY_DB": "E:/repo-memory/nexusmill",
        "REPO_MEMORY_NAME": "Nexusmill",
        "REPO_MEMORY_REPO_ROOT": "C:/Users/User/source/repos/Nexusmill"
      }
    }
  }
}
```

Two ways to carry it, both user-scope:

1. **Append to an existing user-scope plugin's `.mcp.json`** - add the `nexusmill-memory` key
   alongside the plugin's own servers (universal-tools' `.mcp.json` is the model). Quickest, but
   the entry lives in a plugin **cache** dir (`.../plugins/cache/...`) that a plugin update can
   overwrite - re-add it after an update.
2. **A dedicated `repo-memory` plugin** whose `.mcp.json` lists one server per repo you want in
   ZCode, installed through ZCode's normal plugin flow (so `installed_plugins.json` gets a
   `"scope": "user"` row and `config.json` enables it). This keeps repo-memory's mounts in their
   own plugin, out of universal-tools' way, and is the cleaner long-term home. As with every
   mount, point `command`/env at the **canonical** repo-memory venv and DB - never a copy (the
   single-source rule the universal-tools mount already follows).

Whichever you choose, the four `env` vars are the whole contract, exactly as in Part 2.1.

### 3.2 The one ZCode-specific interaction: the G-MEM stub

`arm_repo.py` writes a thin **`AGENTS.md`** global-memory stub in each armed repo (ZCode reads
`AGENTS.md` the way Codex does), and the ZCode skill gate has a **G-MEM** rule that denies work
until that inherited global memory is read. That is the *cross-repo owner context* stack and is
**separate from repo-memory** (which is the *per-repo semantic* store). Both coexist: G-MEM makes
you read the global stub; repo-memory answers repo-specific questions on demand. Do not conflate
them, and do not delete the stub to "clean up" - the gate will refuse.

### 3.3 Verify

Launch ZCode in the repo and confirm the `nexusmill_memory_*` tools are listed and
`nexusmill_memory_stats` returns a path + rows, exactly as in Part 2.2. The GLM backend changes
nothing about this check.

---

## Part 4 - Seeding a repo (do this once per repo, for either harness)

The bootstrap creates the store, seeds it from the repo's markdown, and writes the client config -
run it from repo-memory's venv:

```powershell
$py = "C:\Users\User\source\repos\repo-memory\.venv\Scripts\python.exe"
$env:PYTHONPATH = "C:\Users\User\source\repos\repo-memory"

# writes <repo>/.repo-memory.json + merges <repo>/.mcp.json + creates the LanceDB dir +
# seeds from the repo's markdown. Add --desktop to also register it in the Claude Desktop
# Chat tab (claude_desktop_config.json); drop --desktop to keep it out of Chat.
& $py -B -m repo_memory.bootstrap --repo C:\path\to\MyRepo --index --desktop
```

- The bootstrap is **idempotent and merge-only**: existing MCP servers and config keys survive;
  running it twice changes nothing.
- The repo-root `.mcp.json` it writes is what **Claude Code CLI / Cowork** reads directly (done).
  For **Codex**, copy the four `env` values out of it into a `[mcp_servers.<name>]` + `[.env]`
  block in `~/.codex/config.toml` (Part 2.1). For **ZCode**, copy the server block into a
  user-scope plugin's `.mcp.json` `mcpServers` (Part 3.1) - ZCode does not read the repo file.
  In every case the four env values are identical; only the destination differs.
- **Re-seed** after large doc changes with `python -B -m repo_memory.indexer --repo <path>`
  (or `repo_memory.autoindex --repo <path> --force`). It chunks markdown on `##` headings, purges
  exactly the `docs/...` sources it re-adds, and never touches rows written by an agent's
  `_memory_write`. Use `--dry-run` first.
- Colibri reviews are folded in separately with `python -B -m repo_memory.colibri --repo
  <ScannedRepo> --mirror` - into the scanned repo's store (as `colibri/<mode>` and
  `colibri/<mode>/findings`) and archived into colibri's own store. Run it after a review sweep.

---

## Part 5 - Gotchas that actually bite the client side

- **stdout is the MCP transport.** The server keeps its own prints off stdout on purpose; you do
  not need to do anything, but if you ever wrap or proxy the server, never let anything write to
  its stdout or the client drops the connection mid-handshake.
- **First call after a cold start is slow, the rest are instant.** The embedding model loads
  once. Give Codex a generous `startup_timeout_sec`; Claude Code / ZCode tolerate the wait on the
  first tool call.
- **Scoping differs by harness - know which you have:**

  | Harness | Config surface | Scope |
  | --- | --- | --- |
  | Claude Code CLI / Desktop **Code** tab | project `.mcp.json` | **per-project** (isolated) |
  | **ZCode** (z.ai/GLM) | user-scope **plugin** `.mcp.json` under `~/.zcode/cli/plugins/` | **global** (does NOT read a repo `.mcp.json`) |
  | **Codex** | `~/.codex/config.toml` `[mcp_servers.*]` | **global** (all added repos load every session) |
  | Desktop **Chat** tab | `claude_desktop_config.json` | **global** |

  On any global surface the slug-prefixed tool names are how the model picks the right store -
  they are not decoration.
- **The DB lives on `E:\`.** `REPO_MEMORY_DB` points at `E:\repo-memory\<slug>`. If that drive is
  not mounted, the server starts but every store call fails; check it before debugging config.
- **The registry `E:\repo-memory\_registry.json`** is kept current by the bootstrap and is what
  the colibri hub walks to mirror cross-repo reviews - do not hand-edit it.

---

## Related

- `repo-memory/README.md` - the server's own reference (storage, embeddings, autoindex costs,
  colibri parsing, the setup-from-scratch venv steps, and the hard-won implementation gotchas).
- [CODEX_GATE_IMPLEMENTATION.md](CODEX_GATE_IMPLEMENTATION.md) - the sibling doc for wiring the
  G39 commit gate into Codex (the plugin, `hooks.json`, the deny-guard); the same `~/.codex/` and
  `~/.zcode/` homes appear there.
- `Tools/arm-repo/README.md` - `arm_repo.py`, which arms a repo with the gate + skills + the
  global-memory (G-MEM) stubs that sit alongside repo-memory.
