# Colibri review — src/jcodemunch_mcp/cli/upgrade.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\cli\upgrade.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summaries, artifacts reaudit/jcm/)
- sha256: `1c282b7f89d4b36eceef064acaf3eb541ddc30fd481db710b3413e22b3f8939b` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: the sub-agent's summary (1 CONFIRMED); `_refresh_hooks` 90-110 (preferred `shutil.which("jcodemunch-mcp")`); `run_upgrade` 134-180 (pip runs as `sys.executable -m pip install -U` - the package that was just upgraded is the one `sys.executable -m` loads); `cli/init._hook_invocation` 145-172 (the hook COMMAND path is resolved from PATH inside init itself, independent of which process runs it - so what the choice here changes is whose TEMPLATES/config get written, the very drift #273 exists to cure); the two sibling spawns `cli/hooks.py:117` and `service_installer.py:50` already use `sys.executable -m jcodemunch_mcp`; `tests/test_v1_108_84.py` mocks `_refresh_hooks` whole. No prior `.colibri_reviews` record.

## Verdict
After upgrading THIS interpreter's package, the hook refresh ran whichever `jcodemunch-mcp` was first on PATH - possibly a different, older install, which then wrote its stale templates. Fixed: the running interpreter's module, always.

## Bugs & vulnerabilities
**[LOW] Hook refresh preferred a PATH-resolved binary over the just-upgraded install — CONFIRMED — FIXED** - `line 96-100`
- Trigger (RED on these bytes): a global pipx shim on PATH beside a project venv → `upgrade` pip-upgrades the venv, then runs the shim's `init --hooks`.
- Fix: `init_cmd = [sys.executable, "-m", "jcodemunch_mcp", "init", "--hooks"]` unconditionally (the former fallback), docstring rewritten to say why. The hook command path written by init is unchanged (init resolves it itself).

## Adversarial verification (Phase 3)
- Pinned with `shutil.which` stubbed to a foreign path: the spawned argv starts `[sys.executable, "-m", "jcodemunch_mcp"]`. `run_upgrade`'s pip-absent branch is unaffected (same in-process refresh either way).

## Remediation postscript (same commit)
The fix was applied after this review hashed the bytes above; the file is now `563c9ac32a81584edb107aef000339a46f16a124233ad9cf9c857a2020e55d2a`. TDD: `tests/test_tail_batch4_reaudit.py` (14 tests across the eight files of this batch) - 11 RED on the old bytes (each for its own reason, verified by the per-test failure), 3 controls green throughout, GREEN after.
