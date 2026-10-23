# Colibri review — src/jcodemunch_mcp/hook_event.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\hook_event.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `1410aafa42b9f6318eb85cb256b17f3593135fccc355c05fcfd785b89eefb141` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 3 refuted); the whole 214-line module read end to end - `_resolve_worktree_path` 40-45 (pathlib `/` join of the stdin `name` onto either `worktree_base_path` or `<cwd>/.claude/worktrees`), `handle_hook_event` 82-182 (stdin JSON → `cwd`/`name`/`worktreePath`; `create` runs `git worktree add <resolved> -b worktree-<name>`, `remove` runs `git worktree remove --force` from the main repo root), `_append_manifest`, `read_manifest`; the caller: Claude Code's WorktreeCreate/WorktreeRemove hooks via `jcodemunch-mcp hook-event create|remove` (server.py CLI dispatch) - the payload is authored by whatever drives the harness, not by the operator; `security.validate_path` (the repo's containment idiom: resolve, then check `root in parents`). Tests: `tests/test_watch_claude.py::TestHookEvent` (15; the sub-agent's note "no test file exists" was wrong - it covers create/remove/manifest with mocked `subprocess.run` and mocked `_get_worktree_base`). No prior `.colibri_reviews` record.

## Verdict
The one untrusted string in the payload went into a filesystem path with no containment: a `..` name walked out of the worktrees directory and an absolute name replaced it outright, and `git worktree add` then created a worktree wherever that landed. Fixed before git runs.

## Bugs & vulnerabilities
**[HIGH] `name` from stdin escaped the worktrees directory (traversal, or an absolute path overriding the root) — CONFIRMED — FIXED** - `line 40-45, 134-136`
- What: `Path(root) / name` with `name = "../../escaped"` resolves outside `.claude/worktrees`; with an absolute `name`, pathlib's `/` discards the left operand entirely, so the root was replaced. `handle_hook_event` then `mkdir -p`'d the parent and ran `git worktree add` there (create) or `git worktree remove --force` (remove - refuted as a deletion primitive below, but the manifest still recorded the foreign path). Trigger (audit probe, RED on these bytes): `{"cwd": <repo>, "name": "../../../../escaped_via_traversal"}` and `{"cwd": <repo>, "name": "C:\\Windows\\Temp\\escaped_via_absolute_name"}` both resolved outside the root.
- Fix: `_resolve_worktree_path` resolves the root (configured base, or `<cwd>/.claude/worktrees`) and the candidate, and raises ValueError unless `root in candidate.parents` - a nested name (`team/feature`) stays allowed, the root itself is refused (a worktree is a child, never the directory). `handle_hook_event` catches it for both `create` and `remove` (they share the branch), prints `ERROR: …` to stderr and exits 1 before any mkdir, git call or manifest write. `worktreePath` supplied directly is untouched - Claude Code sends that for a worktree it already owns.

## Refuted (recorded so they are not re-raised)
- `branch_name = f"worktree-{name}"` as git argument injection: always prefixed, never starts with `-`; `subprocess.run` takes a list, no shell.
- `remove` as an arbitrary-path deletion primitive: `git worktree remove` refuses a path not registered under the repo's `.git/worktrees`; an unregistered path is a non-fatal WARNING.
- `_resolve_main_repo`'s `git -C cwd` injectable via `cwd`: a single list element, never shell-interpreted; a bad cwd fails the call and falls back to cwd.

## Missing safeguards (noted, not fixed)
- `_append_manifest` appends without a lock (two hooks racing interleave lines - each line is one `write()` of a small JSON object, so in practice atomic on local filesystems); the name length is unbounded (the filesystem refuses, git refuses - the error is surfaced).

## Adversarial verification (Phase 3)
- Pinned end to end through `handle_hook_event` with the `test_watch_claude.py` fixture shape (stdin patched, `subprocess.run` mocked, base mocked): three traversal spellings, an absolute name, a traversal under a configured base, and the `remove` event all exit 1 with "escapes" on stderr, `subprocess.run` never called, no manifest file created. `_resolve_worktree_path(cwd, ".")` raises.
- Control: a plain name and a nested `team/feature-y` still resolve under `<cwd>/.claude/worktrees`, git is called with that path, both land in the manifest and `read_manifest` returns them.
- `tests/test_watch_claude.py` (all) unchanged and green with the battery.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `fffde4a63f6457d3d42cefa05117b49b5a70ffe68d84dc447b31d5403b673c64`. TDD: `tests/test_hook_event_reaudit.py` (8 tests) - 7 RED on the old bytes, 1 control green throughout, GREEN after. The audit probe passes 2/2 after.
