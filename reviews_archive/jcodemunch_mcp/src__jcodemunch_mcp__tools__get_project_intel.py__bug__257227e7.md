# Colibri review — src/jcodemunch_mcp/tools/get_project_intel.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\tools\get_project_intel.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `257227e76a07fa1fa6c39760cb77c6f708b3cb9875107965a1f32a1c885fd95b` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `_discover_intel_files` 74-160 (`os.walk(walk_root, followlinks=False)` at 99, `_SKIP_DIRS` pruning only, scope resolved with `normpath`+`isdir`), `collect_project_intel` 978-1138 (four per-category parse loops 1017-1095, each parser called bare; returns categories/discoveries/cross_references/discovered_files/file_count/category_count), `get_project_intel` 1145-1227 (scope_path validation 1187-1203: `..` string checks and `isdir` only); the four parsers the probes break (`_parse_github_actions`, `_parse_gitlab_ci`, `_parse_k8s_manifest`, `_parse_pyproject_scripts`: `.items()` / `.get()` / `.startswith()` on YAML/TOML values of the wrong shape); this venv is Python 3.11 (`os.path.isjunction` arrives in 3.12; the package supports 3.10+), and the probe demonstrated that `os.walk(followlinks=False)` DOES descend a junction on Windows; existing `tests/test_project_intel.py` (62 tests); both RED probes re-run on these bytes (probe 1: 4/4 FAIL, probe 3: 2/2 FAIL - and its INFO line showed the UNSCOPED walk leaking through the junction too).

## Verdict
One odd file sank the whole report, and the discovery walk followed a junction out of the repository - unscoped as well as scoped. Both findings confirmed and fixed; the second more broadly than reported.

## Bugs & vulnerabilities
**[HIGH] the discovery walk leaves source_root through a symlink/junction — CONFIRMED (broader than reported) — FIXED** - `line 91-101, 1195-1201`
- What: the sub-agent reported `scope_path` naming a junction; the probe's own INFO line showed the plain unscoped walk discovering the same two files under the junction, because `os.walk(followlinks=False)` only stops at what `os.path.islink` recognises and on Windows before 3.12 that excludes junctions. Files outside the indexed tree were reported and PARSED - `.env.example` contents from outside the repository came back as `env_vars`.
- Fix (in the walk, so every caller of `collect_project_intel` is covered, not only `get_project_intel`): `_is_reparse_point()` (symlink, or on Windows the `FILE_ATTRIBUTE_REPARSE_POINT` bit from `lstat`, which needs no 3.12 API) and `_inside()` (`realpath` containment, `normcase`d) prune every directory entry that is a link/junction or resolves outside the real root; a scope that is one, or resolves outside, discovers nothing (warning logged). `get_project_intel` additionally refuses such a scope up front with an explicit error (the sub-agent's snippet, plus the reparse check). Pruning reparse points outright also removes the junction-cycle hang that `followlinks=False` did not prevent here.

**[HIGH] a shape-valid-but-unexpected CI / K8s / TOML file raised out of `collect_project_intel` and took every category down — CONFIRMED — FIXED** - `line 1017-1095`
- What: `jobs:` as a list, `[project] scripts` as a list, a scalar `metadata`, an integer top-level key in `.gitlab-ci.yml` - each YAML/TOML-valid, each an AttributeError/ValueError inside its parser with no per-file isolation, so one stray file in a monorepo emptied the whole report. Probe 1 reproduced all four.
- Fix: each per-file parse is isolated; a failure is logged at debug AND named in a new `parse_failures` list (returned by `collect_project_intel`; surfaced on the tool response only when non-empty) - the omission is visible to the reader, never silent. The healthy siblings parse.

## Missing safeguards
- The per-file cap (`_MAX_INTEL_FILES`) counts intel files only; the walk visits every directory of the tree before reaching it. Bounded by the repository now that links are pruned; noted.

## Adversarial verification (Phase 3)
- The battery builds the junction (`_winapi.CreateJunction`) on Windows and a symlink elsewhere, then asserts on `discovered_files` realpaths AND on the parsed `env_vars`/`dockerfiles` content: nothing from outside, the inside Dockerfile still reported; the scoped call over the link discovers zero files; `get_project_intel` refuses the scope with `load_view`/`resolve_repo` stood in.
- The four shape-invalid cases are parametrised with a healthy sibling each: the sibling parses and `parse_failures` names exactly the bad file; a clean tree yields an empty list (no noise).
- `tests/test_project_intel.py` (62) unchanged and green with the battery: 70 passed.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `933b2e467ede5449f6ed50b6422387cf37501ce6780453b010571de1aeff6611`. TDD: `tests/test_get_project_intel_reaudit.py` (8 tests) - all 8 RED on the old bytes (seven on behaviour, the clean-tree check on the missing key), GREEN after; probes 1 and 3 ALL PASS.
