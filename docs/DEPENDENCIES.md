# DEPENDENCIES — what a new user needs to run the distributed pieces

**Scope (owner order 2026-10-11):** the three distribution surfaces — the
**adversary-gate** plugin (the gate suite, `colibri-marketplace/plugins/adversary-gate`,
v0.3.7), the **colibri-review** plugin (`colibri-marketplace/plugins/colibri-review`,
v0.4.1), and this **colibri-code-review** repo (the console + its tooling). Every
claim below was surveyed from the current bytes (imports, URLs, env keys, hook
scripts) on 2026-10-11 — not from memory.

---

## 1. adversary-gate plugin (the commit gate)

### Runtime requirements
| dependency | requirement | notes |
|---|---|---|
| **Python** | 3.9+ recommended (3.11 used in dev) | stdlib only for the core; no `pip install` needed. The vendored code has no 3.10+-only syntax in the shipped modules. |
| **Git** | any maintained git for hooksPath arming; **2.54+** for config-based-hooks arming (`config_hooks.py` is NOT vendored in the plugin — it is the author-machine migration tool; plugin users arm via `install_gate.py`, which works on any git with `core.hooksPath`) | `GIT` falls back from the hard-coded `C:\Program Files\Git\cmd\git.exe` to `git` on PATH. |
| **Network** | `https://openrouter.ai/api/...` (chat/completions, batches, models, decisions) | Reviews ride OpenRouter. |
| **API key** | `OPENROUTER_API_KEY` (required for reviews); `XAI_API_KEY` (optional grok backup; also read from a `.env` `xaikey=` on the author machine) | No key → the gate fails CLOSED (no commit without an external CLEAR, by design). |
| **Optional: local LLM** | `ADVERSARY_LOCAL_URL` pointing at an Ollama-compatible endpoint | the $0 local rung; entirely optional. |
| **Optional: `tree_sitter_language_pack`** | `pip install tree-sitter-language-pack` | Guarded import — without it, the oversize-file enclosing-symbol window falls back to Python-AST/line heuristics for non-Python files. The gate works without it. |

### Configuration surface (all optional env keys, surveyed from the bytes)
`ADVERSARY_MODEL` (the review chain — default tiered: deepseek-v4.1-flash →
hy4-preview → kimi-k2.7-code via OpenRouter pins), `ADVERSARY_MAX_TOKENS`,
`ADVERSARY_TIER1_TIMEOUT` / `ADVERSARY_TIER2_TIMEOUT`, `ADVERSARY_AUDIT_PCT`,
`ADVERSARY_AUDIT_MODEL`, `ADVERSARY_LOCAL_URL` / `ADVERSARY_LOCAL_MIN_FREE_MIB`,
`ADVERSARY_WARN_OFF`, `ADVERSARY_PROMOTE_*`, `ADVERSARY_JEV_*`,
`ADVERSARY_PREGATE_*`, `ADVERSARY_ADJUDICATE_OFF`, `ADVERSARY_FAKE*` (testing).

### Platform notes
- The hook shims resolve Python as `python311` hard path → `python3` → `python`
  and resolve the suite from `$0` (relocatable). Developed and tested on
  Windows (git-bash hooks); the shims are POSIX `sh` — they run under git's
  bundled bash on Windows and on POSIX.
- Layer-2 harness guards (`harness_guard.py` shipped inside the plugin's
  `adversary_gate.py` integration) are harness-side; Codex-side policy
  (`codex_*`) is NOT part of the plugin distribution (author-machine only).

### Certified runtime - SHIPPED since plugin 0.3.8 (owner order 2026-10-11 port)
`runtime_loader.py`, `enforcement_runtime.py`, and `config_hooks.py` now ship
in the plugin, LAYOUT-DERIVED so the same bytes run at the author suite and
in the plugin tree (derivation proven in place; EV-200). `reviewed_write.py`
and the `codex_*` pair remain author-machine-only (Codex harness integration
and broker machinery); imports are guarded so the plugin core runs
standalone without them.

---

## 2. colibri-review plugin (the review skill)

| dependency | requirement | notes |
|---|---|---|
| **Harness** | Claude Code (or a compatible harness with plugin + skill + SessionStart-hook support) | the skill text IS the product; the plugin adds a SessionStart doctrine injection. |
| **SessionStart hook** | `hooks/session-start.cmd` — a Windows batch `type` of `doctrine.md` | Windows-only as shipped; on other platforms it fails silently (guarded `2>nul` + `exit /b 0`) — the doctrine just won't auto-inject. A POSIX `.sh` twin would be the fix if POSIX distribution matters. |
| **jCodemunch MCP** | strongly recommended (the skill's law: jCodemunch is the ONLY code-search path) | separate distribution (`jcodemunch-mcp`); without it the skill's search law cannot be followed as written. |
| **hy4-review CLI** | OPTIONAL (the optional external second-opinion pass) | lives in `Tools/hy4-review`; stdlib-only Python; needs `OPENROUTER_API_KEY` (or `Open_Router_Token` in the author's `.env` — machine-specific, not portable). |
| **repo-memory store** | optional (G40 discipline) | separate plugin. |

---

## 3. colibri-code-review repo (this repo — the console)

| dependency | requirement | notes |
|---|---|---|
| **Python** | 3.10+ | uses `str.removeprefix` and friends; dev on 3.11. |
| **pip packages** | `requirements.txt`: `streamlit`, `openai`, `pandas`, `pyflakes`, `mypy` | the console (`app.py`/`ui.py` = Streamlit), the analyzer (`openai`), error-rate reports (`pandas`). `pyflakes`/`mypy` power `static_context.py`. |
| **Dev/test only** | `pytest` (not in requirements.txt — tests import it) | add to a dev extra if running the test suite. |
| **`openai` key** | the analyzer's own client (separate from the gate's OpenRouter usage) | check `analyzer.py` for its env contract at integration time. |

---

## Quick-start for a new user (minimum viable)

1. **Gate only:** Python 3.9+, git, `OPENROUTER_API_KEY` set. Install the
   `adversary-gate` plugin, run `python tools/install_gate.py <repo>` in each
   repo you want gated. Commits now require an external CLEAR (paid — budget
   ~$0.01–0.30 per review round depending on payload and tier).
2. **+ Review skill:** install the `colibri-review` plugin (Claude Code).
   Add the jCodemunch MCP for the full skill discipline. The optional
   `hy4-review` pass needs its own `OPENROUTER_API_KEY`.
3. **+ Console:** clone this repo, `pip install -r requirements.txt`,
   `streamlit run app.py`.

**Surveyed 2026-10-11 from:** `plugins/adversary-gate/tools/*.py` (AST import
walk: stdlib-only core + guarded `tree_sitter_language_pack`; URL/env scans),
`plugins/colibri-review/` (hooks.json + session-start.cmd + SKILL.md external
references), `Tools/hy4-review/hy4_review.py`, this repo's AST walk +
`requirements.txt`.
