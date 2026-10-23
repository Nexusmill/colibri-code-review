# Colibri review — src/jcodemunch_mcp/tools/get_file_tree.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_file_tree.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `397ff25472db134b6c40bdac37368cc5990bce5e973cb40189fb2eb72da23418` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `get_file_tree` 33-106 (prefix filter at 52: bare `startswith`; the relative path in `_build_tree` is `file_path[len(path_prefix):].lstrip("/")`, so a sibling match also produced a garbled relative path), `_build_tree` 109-143 (dict-of-dicts; a file node stored under a name later navigated as a directory -> `["children"]` KeyError), `_dict_to_list` 146-160; `index.source_files` is trusted (one filesystem cannot hold both `src/foo` and `src/foo/bar.py`, but composed/overlay indexes - branch deltas, cross-repo merges - build the list programmatically); `tests/test_get_file_tree.py` (10); the audit probe re-run on these bytes (2/2 FAIL). No prior `.colibri_reviews` record.

## Verdict
A scoped tree query leaked sibling directories and a malformed file list crashed the tool. Both confirmed and fixed; the sub-agent's two self-refutations re-checked and kept.

## Bugs & vulnerabilities
**[MEDIUM] `path_prefix` had no path-segment boundary — CONFIRMED — FIXED** - `line 52`
- What: `path_prefix="src"` returned `src_other/leak.py` beside `src/mod.py` (probe), and the relative path computed by slicing `len(path_prefix)` off the leaked file was garbled (`_other/leak.py`). Within the trusted `source_files` set - a scoping error, not a boundary break.
- Fix: the prefix is matched at a segment boundary (`f == prefix` or `f.startswith(prefix + "/")`; a trailing slash is tolerated; an empty prefix means everything). Pinned for `src`, `src/`, `""` and an exact file path.

**[MEDIUM] `_build_tree` raised KeyError on a file/directory name collision — CONFIRMED — FIXED** - `line 138-140`
- What: `["src/foo", "src/foo/bar.py"]` stored `foo` as a file node, then navigated it as a directory and indexed `["children"]` - the whole read-only tool failed instead of degrading.
- Fix: the directory wins (its subtree carries more): a file placed where a directory node exists is skipped; a directory navigated through a non-directory node replaces it. Pinned in both orders; a normal tree is unchanged.

## Refuted (sub-agent's own, re-checked and agreed)
- `max(1, max_files)` raising on a non-numeric config value: the config layer is typed and out of scope; no evidence of a non-numeric value for a numeric key.
- `len(str(tree).encode())` failing on non-UTF-8 content: every string here is an already-decoded `str`.

## Adversarial verification (Phase 3)
- The prefix test indexes a real two-directory repo and asserts the exact file list for four prefix shapes, including the exact-file prefix that the segment rule must still admit.
- The collision test feeds both orders (file first, directory first) through the real `_build_tree` with a stand-in index.
- `tests/test_get_file_tree.py` (10) unchanged: 13 passed with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `7c8ac4945a6b3f9677bf1e897aaf4c7e857d4d2deee95edcf42bfcfd41babaaf`. TDD: `tests/test_get_file_tree_reaudit.py` (4 tests) - 2 RED on the old bytes, 1 control green throughout, GREEN after; the audit probe ALL PASS.

**Gate catch (round 1, gate_20260913-173112, LOW-MEDIUM, accepted):** the prefix was normalised for the FILTER but `_build_tree` was still handed the raw prefix and sliced `len(path_prefix)` off each path - with `"src//"` (a `dir + "/"` double-join) every relative path lost a character, and two files that then collided (`src/x/a.py`, `src/y/a.py` -> `a.py`) silently merged with no flag; the old bytes returned an empty tree for that input. My own pins (`src`, `src/`, `""`, exact file) missed the class - `src/` only works because one slash is what the normalisation removes. Fixed: `_build_tree` normalises the prefix itself and slices by that; pinned by `test_a_doubled_trailing_slash_keeps_structure_and_every_file` (RED on the round-1 bytes) and by `src//` / `src///` yielding the baseline tree end to end. Docketed as EV-076.
