# Colibri review — src/jcodemunch_mcp/tools/find_dead_code.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\find_dead_code.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `34261a22c364f8fb02ac727cf6983c7bc982e8824bef621a18fcec80c087576e` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED); `_package_json_entries` 106-164, the candidate loop 150-151 (`cand.lstrip("./")`); the backported twin `get_dead_code_v2._package_json_entries` 205-269 (same loop, 254-255 - fixed in the same commit, its own DELTA record); the class already fixed today in `handoff.py` 104 and `evidence/producers.py` 84 (and documented at `storage/token_tracker.py` 95); the remaining sites of the same class, OUT of this batch: `audit_agent_config.py` 188/434 (recorded LOW 2026-09-05, unfixed), `get_project_intel.py` 905/951, `index_folder.py` 1018, `list_workspaces.py` 422, `benchmarks/deadcode_eval/run_eval.py` 28. No prior `.colibri_reviews` record.

## Verdict
`lstrip("./")` is a character class: a `package.json` entry point under a dot-directory lost its dot, never matched a source file, and the library's real entry point looked dead. Fixed in this file and its twin.

## Bugs & vulnerabilities
**[LOW] `lstrip("./")` ate the dot of `./.github/x` (and any `./.dotdir/`) — CONFIRMED — FIXED** - `line 151`
- Trigger (RED on these bytes): `"main": "./.github/scripts/run.js"` with that file indexed → not an entry; `./.hidden/cli.js` under `pkg/` → not an entry.
- Fix: normalise slashes, then strip literal `./` prefixes in a loop (a repeated `././x` also resolves). A `../x` candidate was never resolved correctly (the old strip turned it into a sibling path, the new code leaves it unmatched) - unchanged outcome, noted.

## Adversarial verification (Phase 3)
- Pinned on a fake index/store for BOTH modules: `{".github/scripts/run.js", "src/index.js", "pkg/.hidden/cli.js"}` resolved; the plain `./src/index.js` case unchanged.

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `a18b626214e690d2609656d2a848b3c079e256c512cb699ac665fcac0e59779a`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
