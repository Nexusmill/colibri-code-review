# Debug: jcodemunch fork — markdown/html symbols silently absent in production

- **Source:** `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\parser\extractor.py` (gate at line 284) + `~/.code-index/config.jsonc` (`languages` allowlist)
- **Model:** claude-fable-5 (in-session) · **Mode:** debug (colibri Phase D) · **Date:** 2026-08-12
- **sha256(extractor.py):** `359c0eabb6b395f7b9644b71e9b39e3a87d68c3b47dac90a9f8c181f683db247`
- **Context pack:** jcodemunch outlines/search over the fork repo (watcher.py, index_folder.py,
  _indexing_pipeline.py, parse_cache.py, config.py, tests/test_markdown.py); production server
  process identity via PowerShell (pid 63972 command line); live probes through the production
  MCP server (index_folder on a scratch corpus, watcher edit probe on docs/*.md).

## Failure signal (reproduced first)
`get_file_outline` on every `docs/*.md` in `Nexusmill/nexusmill` returned `symbols: []`;
a brand-new md file (2 ATX headings) indexed via the production server's FULL `index_folder`
came back `symbol_count: 0`, `no_symbols_files: [probe.md]` — while `search_text` hit the
same files and `pytest tests/test_markdown.py` was 5/5 green in the same venv.

## Hypothesis ledger (checked top-down, one variable at a time)
1. venv build lacks the fork commits — **killed**: editable install, module file resolves to
   the working tree, `MARKDOWN_SPEC` present, exe `--version` = 1.108.272.
2. `.md` not mapped to markdown at runtime — **killed**: `LANGUAGE_EXTENSIONS['.md'] == 'markdown'`,
   outline responses report `language: markdown`.
3. Stale incremental index (files unchanged since old server) — **killed**: a NEW file and a
   watcher-reindexed file both produced zero symbols.
4. Incremental/watcher path differs from full path — **killed**: full `index_folder` on a fresh
   scratch corpus also produced zero symbols.
5. Server-process environment — **killed**: reproduced OUTSIDE the server: direct
   `parse_file(fixture, 'sample.md', 'markdown')` in the venv returned `[]` while the same call
   inside pytest returns 4 sections.
6. **CONFIRMED root cause:** `parse_file` consults `is_language_enabled(language, repo=repo)`
   (extractor.py:284) and returns `[]` when the language is not allowlisted. The auto-generated
   `languages` array in `~/.code-index/config.jsonc` held all 72 upstream languages and neither
   `markdown` nor `html` (the two fork additions). pytest never loads that user config, which is
   why tests pass and Task 4's isolated dev verification passed.

## Fix (root cause, both layers)
- `markdown` + `html` inserted alphabetically into the global `languages` allowlist
  (write→fsync→reread→verify). Global config is only read at server startup.
- Committed `Nexusmill/.jcodemunch.jsonc` with `"languages": null` (all enabled) — project
  config resolves live per read, so the RUNNING server honored it immediately.

## Verification (reproducer re-run)
- Scratch corpus re-index through the production server: `symbol_count: 3` (was 0).
- Full `index_folder` on Nexusmill: **5,153 → 7,563 symbols**, 295 markdown files.
- `docs/AGENT_STATE.md` (274KB) outlines into sections; single-section `get_symbol_source`
  ≈400 tokens. Watcher debounce reindex proven separately (quartz-heron probe).

## Residual
Two stale pre-fork servers (pids 37688/20720, v1.108.193/.198) can strip a md file's section
symbols if their sessions reindex it; self-heals on next fork-watcher touch. The allowlist is
adaptive (`apply_adaptive_languages`) — the repo-root `.jcodemunch.jsonc` is the standing guard.
