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

**ZCode is Claude Code family.** It runs the Claude Code agent loop on the z.ai coding plan
(`builtin:zai-coding-plan/GLM-5.3`), rooted at **`~/.zcode/cli/`**, with global plugin hooks (the
universal-tools plugin) rather than per-repo settings. Because MCP is model-agnostic, **repo-memory
needs no GLM-specific work**: the same server, the same four tools, the same data.

### 3.1 The wiring ZCode already understands

ZCode, like Claude Code CLI, reads a project **`.mcp.json`** at the repo root. The bootstrap
(Part 4) writes exactly that file, so **arming a repo for Claude Code arms it for ZCode at the
same time** - the server block is identical:

```json
{
  "mcpServers": {
    "nexusmill-memory": {
      "type": "stdio",
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

This is a **merge** target: the bootstrap adds/updates only its own server key and leaves every
other MCP server in the file intact.

> **Confirm which config surface your ZCode build reads.** If your ZCode reads the project
> `.mcp.json` (the Claude Code CLI default), you are done after the bootstrap - it is per-project
> and isolated. If your build instead registers MCP servers in a **global** file under
> `~/.zcode/` (the way Codex uses `config.toml` and the way the Claude **Desktop Chat** tab uses
> `claude_desktop_config.json`), add the same server block there and treat it as global (slug
> prefixes disambiguate, add only the repos you work in). Check with one look: if the repo root
> has a `.mcp.json` and ZCode lists the `<slug>_memory_*` tools when launched in that repo, it is
> reading the project file.

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
- For **Codex**, copy the four `env` values from the `.mcp.json` it writes into a
  `[mcp_servers.<name>]` + `[.env]` block in `~/.codex/config.toml` (Part 2.1). For **ZCode**, the
  `.mcp.json` it writes is already what ZCode reads (Part 3.1) - nothing more to do unless your
  build uses a global registry.
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
  | **ZCode** (z.ai/GLM) | project `.mcp.json` (or a global `~/.zcode/` registry) | per-project, unless your build is global |
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
