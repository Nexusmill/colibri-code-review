# Colibri review — src/jcodemunch_mcp/tools/index_file.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\index_file.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `d321af498a8cc7a3caf0496bbcf070cd2bee98f0d08d1817b399dbc464b9969e` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED with a RED probe, 1 PLAUSIBLE, 1 refuted); `index_file` 58-260: containment (`validate_path`), the #351 eligibility block 136-150 (`is_secret_file` and nothing else), the language check, the branch-delta routing 171-189; `index_folder._should_index_file` 471-604 ("single source of truth for per-file index-eligibility checks … any new filter added to indexing MUST land here so both paths apply it", #306) and the watcher fast path's inline construction of its filter bundle 1699-1774 (`get_extra_ignore_patterns`, root `.gitignore`, `get_max_file_size`, the #25 forced-path scan, `_build_skip_dirs_regex`, `get_respect_cachedir_tag`); `tests/test_index_file.py` (8), `tests/test_v1_108_78.py::test_index_file_refuses_real_credential_file` (pins `skipped == "secret"`). index_folder.py's own record (18b712cf) stands; this commit extracts one helper from it. No prior `.colibri_reviews` record for index_file.py.

## Verdict
The third indexing entry point applied one of thirteen filters. Every non-secret skip the walk enforces was open to a hook-driven `index_file` - the file appeared, and the next full walk pruned it. Fixed by giving the entry point the same bundle the fast path builds, from one builder.

## Bugs & vulnerabilities
**[MEDIUM] `index_file` checked `is_secret_file` alone, reopening the #351 flip-flop for every other filter — CONFIRMED — FIXED** - `line 136-150`
- What: `node_modules/x.js` (a skipped directory), a gitignored build output, a file matching an extra ignore pattern, an oversize file, a file under a `CACHEDIR.TAG` directory or inside a nested worktree - all refused by the walk and by the watcher fast path through `_should_index_file`, all accepted here. Trigger (audit probe, RED on these bytes): `index_file` on `node_modules/somepkg/vendored.py` under an indexed folder → `success: True`, the symbol indexed; the next full walk drops it.
- Fix: `index_folder.fast_path_filters(folder_path, walk_root, *, follow_symlinks, max_size, extra_ignore_patterns, candidate_paths)` - the watcher fast path's inline bundle construction lifted verbatim into one builder that returns `(cfg, gitignore_specs)`; the fast path now calls it (behaviour byte-identical: same extra-pattern spec, root-level `.gitignore` only, the #25 forced-path scan paid only when a candidate is over the cap, `check_binary=False`, `check_filename=True`, the project-scoped size cap and CACHEDIR.TAG setting); `index_file` calls it with the file as the one candidate and runs `_should_index_file`, refusing with the walk's own reason in `skipped` (`skip_dir`, `gitignore`, `extra_ignore`, `too_large`, `cache_dir`, `nested_worktree`, `secret`, …) and the same "would not survive the next full index" sentence. The language check keeps its place and message. `is_secret_file` is no longer imported here - the bundle's step 10 is the same call.

## Deferred / PLAUSIBLE (not fixed here)
- **[MEDIUM, PLAUSIBLE] branch-delta routing:** a base index whose `branch` field is empty is treated as already-current-branch (`_base_branch = _current_branch`), so on a repo whose base was indexed before branch tracking existed, feature-branch edits may write into the shared base index instead of a delta. Unverified because it needs a pre-branch-tracking base index under a checked-out feature branch; the fix belongs with the branch-tracking owner (index_store/sqlite_store), not this unit.

## Refuted (recorded so it is not re-raised)
- `../` escape via `rel_path` computed before validation: `validate_path(source_root, file_path)` runs first and `file_path` is already resolved.

## Adversarial verification (Phase 3)
- Pinned end to end through `index_file` over a real `index_folder` index: a file under `node_modules/` → `skipped == "skip_dir"`; a file under a root-`.gitignore`d `build/` → `skipped == "gitignore"`; in both, `search_symbols` afterwards finds nothing - the index was not touched.
- Controls: a plain new file still indexes and is searchable; a real credential file still reads `skipped == "secret"` (the v1.108.78 pin, unchanged).
- The watcher fast path is exercised by the existing suite through `index_folder(changed_paths=…)`; the extraction changed no filter input (traced line by line against the old block).

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `eaf63376fb846c2696ea22f267005d58dcea2285910205b3a6b28f24fec981af`, and `tools/index_folder.py` (helper extracted, fast path re-pointed) is `d38a5136483b2463cb44257825ec7e8aa0b88f91bd1180bac293c66bc7a0cb80`. TDD: `tests/test_index_file_eligibility_reaudit.py` (3 tests) - 2 RED on the old bytes, 1 control green throughout, GREEN after. The audit probe passes 3/3 after.
