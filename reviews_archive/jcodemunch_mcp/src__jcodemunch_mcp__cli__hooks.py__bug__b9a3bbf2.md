# Colibri review — src/jcodemunch_mcp/cli/hooks.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\cli\hooks.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `b9a3bbf2d71f0099ef1bba49ffcd567a3a01bf54b5e7dc235e0076032a5ba2e9` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the hook entry points (`run_posttooluse` 342-385 and `run_copilot_posttooluse` 388-457 both `Popen(["jcodemunch-mcp", "index-file", ...])`; `_load_snapshot` 466-508 already reads the live journal via `snapshot_from_live` for PreCompact; `_build_landmark_section` 597-700; `run_taskcomplete` 730-897; `run_subagentstart` 904-990; `_MIN_SIZE_BYTES` at import, line 86); the store: `IndexStore.__init__` (index_store.py 383-392: defaults to `~/.code-index`, never reads `CODE_INDEX_PATH`) vs `session_state._live_journal_path` (258-261: honours `CODE_INDEX_PATH`) and the server (`storage_path = os.environ.get("CODE_INDEX_PATH")`); `SQLiteIndexStore._list_repo_from_db` 2537-2622 (entries carry `repo`, `source_root`, ... - never `owner`/`name`, verified live: a fresh index lists as `{"repo": "local/repo-...", ...}`); Windows `CreateProcess` search order, verified by probe on this box (a `cmd.exe` renamed `jcodemunch-mcp.exe` in the parent's cwd is executed by `Popen(["jcodemunch-mcp", ...])` once the Git-Bash `NoDefaultCurrentDirectoryInExePath` variable is absent; with it set, PATH wins); existing `tests/test_hooks.py`, `test_copilot_hook.py`, `test_post_tool_use_hook.py` + 5 more (141); the audit probe re-run on these bytes (2 FAIL of 6). No prior `.colibri_reviews` record.

## Verdict
Three hook features had never worked against a real store, the PostToolUse indexer could be hijacked by a file in the repository being edited, and one bad env var took every hook down at import. Confirmed: the sub-agent's two findings, its two PLAUSIBLE items (one upgraded to HIGH on reproduction), and two further defects found in the same function.

## Bugs & vulnerabilities
**[HIGH] both PostToolUse hooks spawn the indexer by bare name - on Windows a repository can plant the executable — CONFIRMED (upgraded from the sub-agent's PLAUSIBLE LOW) — FIXED** - `line 378-381, 450-453`
- What: `Popen(["jcodemunch-mcp", "index-file", path])`. The hook runs with the project directory as cwd; `CreateProcess` resolves a bare name from the parent's current directory BEFORE `PATH` unless `NoDefaultCurrentDirectoryInExePath` is set (Git-Bash sets it; a plain Windows session does not). Reproduced: a renamed `cmd.exe` at the cwd ran in place of the CLI. A repository shipping `jcodemunch-mcp.exe` at its root therefore executes on every edit an agent makes in it.
- Fix: `_spawn_index_file()` runs `[sys.executable, "-m", "jcodemunch_mcp", "index-file", path]` - absolute, and the same install the hook is running from; both hooks use it; no `sys.executable` -> no spawn. Two existing tests that pinned the bare-name argv were updated.

**[MEDIUM] `run_taskcomplete` read the in-process journal - always empty in a hook subprocess — CONFIRMED — FIXED** - `line 751-760`
- What: the #334 process boundary `run_precompact` crosses via the live journal; this hook never did, so TaskCompleted diagnostics never fired. Probe: PreCompact reported the live-journal edit, TaskCompleted emitted nothing.
- Fix: `load_live_journal()` first (the file the server persists under `CODE_INDEX_PATH`), the in-process journal as the embedded-invocation fallback.

**[MEDIUM] `list_repos()` entries carry `repo`, not `owner`/`name` - three hook loops skipped every repository — CONFIRMED (new, found while fixing the above) — FIXED** - `line 647-651, 795-800, 931-936`
- What: `_build_landmark_section`, `run_taskcomplete` and `run_subagentstart` all did `entry.get("owner")` / `entry.get("name")` and `continue`d on empty - and the store never returns those keys (`_list_repo_from_db` builds `repo`, `source_root`, ...). The PreCompact landmarks, the TaskCompleted diagnostics and the SubagentStart briefing were dead against any real store; the one test that fed SubagentStart a repo used a mock shaped like the assumption (`[{"owner": "test", "name": "repo"}]`). Same class as the file's own #406 comment: a caller reading a shape the callee does not produce.
- Fix: `_repo_owner_name(entry)` splits `repo` on the first `/` (and still accepts `owner`/`name` if a caller supplies them); all three loops use it.

**[MEDIUM] the hooks opened `IndexStore()` - `~/.code-index` regardless of `CODE_INDEX_PATH` — CONFIRMED (new) — FIXED** - `line 301, 640, 788, 921`
- What: `IndexStore.__init__` never reads the env var; the server, the tools and the live journal do. On a box with `CODE_INDEX_PATH` set, every hook looked at a store the server never wrote (and `run_taskcomplete`'s `find_dead_code` / `get_untested_symbols` / `check_references` calls passed no `storage_path`, so they did too).
- Fix: `_hook_store()` / `_hook_storage_path()` open the `CODE_INDEX_PATH` store and pass it to the three tool calls.

**[LOW] a non-integer `JCODEMUNCH_HOOK_MIN_SIZE` crashed every hook subcommand at import — CONFIRMED — FIXED** - `line 86`
- Fix: `try/except (TypeError, ValueError)` -> default 4096.

**[LOW] `run_posttooluse` assumed `tool_input` is a dict — CONFIRMED (the sub-agent's PLAUSIBLE) — FIXED** - `line 360`
- A `null` `tool_input` raised AttributeError (non-zero exit, a hook error surfaced to the user). Now `isinstance` guarded, and `file_path` must be a non-empty string.

## Adversarial verification (Phase 3)
- The CreateProcess claim was reproduced three ways on this box before being called HIGH: with the Git-Bash variable present the real CLI ran (rc 2 usage error); with it removed the planted binary ran (rc 0, `ver` output); an explicit path ran it either way.
- `_repo_owner_name` is pinned on the real entry shape, the legacy mock shape, a slash-less `repo` and an empty entry; the SubagentStart test feeds a REAL-shaped entry through a stand-in store and also asserts the store was opened with `CODE_INDEX_PATH`.
- The TaskCompleted test indexes a real repo into a scratch store, persists a server-side journal there, proves this process's journal is empty, and asserts the diagnostics message - end to end through the fixed store, entry shape and journal.
- The whole battery was run against the pre-fix bytes via a stash: 7 of 7 RED; 7 of 7 GREEN after. The 8 existing hook test files: 148 passed with the battery (two argv pins updated).

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `749b854d165e5905133a0575829e1d1f222d994cf9912d2f28d2396f9a34718d`. TDD: `tests/test_cli_hooks_reaudit.py` (7 tests) - 7 RED on the old bytes, GREEN after; the audit probe ALL PASS.
