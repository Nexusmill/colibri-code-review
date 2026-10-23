# Colibri review — src/jcodemunch_mcp/credentials.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\credentials.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `e044d55f4f5e0240123d943db7f0458605bf216337e8b12d44b82cfc8ceb017b` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: `CREDENTIAL_ENV_VARS` 63-74 (documented as the canonical list: "add to this list when introducing a new credential surface"), `resolve_credentials_in_env` 145-200 (rewrites `keyring:NAME` values in place, fail-closed on a missing package/entry), `list_recognised_env_vars` 82 (feeds `config --check`, server.py 8280); consumers of the names: `org/license.py` 91 reads `JCODEMUNCH_LICENSE_KEY`; `GH_TOKEN` is read ONLY by `groq/config.py` 36 (the retired groq surface, flag-only per the owner); `service_installer._is_secret_env` imports this list (its explicit `JCODEMUNCH_LICENSE_KEY` special case becomes redundant but stays as belt-and-braces); `tests/test_credentials.py::test_canonical_list_matches_documented_surface` LOCKS the set "so any future change is forced through CHANGELOG"; the audit probe re-run on these bytes (2/3 FAIL). No prior `.colibri_reviews` record.

## Verdict
The canonical credential list was one name short of the credentials the server actually reads. Fixed; the second name the audit proposed is declined with a reason.

## Bugs & vulnerabilities
**[MEDIUM-HIGH] `CREDENTIAL_ENV_VARS` omits `JCODEMUNCH_LICENSE_KEY` — CONFIRMED — FIXED** - `line 63-74`
- What: a `keyring:NAME` reference in `JCODEMUNCH_LICENSE_KEY` was never resolved, so the literal prefix reached the license check (and `config --check` did not list the variable). Probe: the control (`GROQ_API_KEY`) resolved, the license key did not.
- Fix: the name added to the canonical list, with the locked test updated and a CHANGELOG `[Unreleased]` entry in the same commit (the test's own rule).

## Declined
- **`GH_TOKEN` (the audit's second MEDIUM).** Its only in-tree consumer is `groq/config.py` - the groq surface the owner retired on 2026-08-02 (flag, don't fix). Adding a name whose sole consumer is retired code is dead weight in a list that is meant to be exact. Recorded in the CHANGELOG entry; the probe's third check therefore still fails, by decision.

## Refuted (sub-agent's own, re-checked and agreed)
- `OPENAI_API_BASE` being a URL, not a secret, is a harmless mismatch: resolution only acts on values literally prefixed `keyring:`.
- The `except Exception` around `get_password` cannot leave a partial value: on exception the loop `continue`s without writing `os.environ` (fail-closed as documented).

## Adversarial verification (Phase 3)
- The battery resolves a `keyring:` reference through a fake in-process keyring module (`sys.modules["keyring"]`, monkeypatched) and asserts the resolved value AND `get_keyring_source_for`, with `GROQ_API_KEY` as the already-recognised control.
- `tests/test_credentials.py` (13 + the locked-set test updated), `test_service_installer_reaudit.py`, `test_config_check*.py`: 34 passed, 1 skipped with the battery.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `5c9b131027514a446aa321ada291ea7580cb54513bc630a39e7b4c77a9fbb2de`. TDD: `tests/test_credentials_reaudit.py` (2 tests) - both RED on the old bytes, GREEN after; the audit probe passes its license-key check and fails only the declined `GH_TOKEN` check.

**Gate catch (round 1, gate_20260913-165100, LOW-MEDIUM tests-only, accepted):** the new battery let `resolve_credentials_in_env` write `credentials._resolution_source` and never cleared it - the sibling `tests/test_credentials.py` isolates that global with an autouse fixture, but on ITS module instance (it imports `src.jcodemunch_mcp.credentials`, a second copy of the module), so the `jcodemunch_mcp.credentials` instance this battery and the server use carried `GROQ_API_KEY -> groq`, `JCODEMUNCH_LICENSE_KEY -> lic` into every later-collected module (`get_keyring_source_for` feeds `config --check`). Order-dependent, not clean. An autouse fixture now clears the env names and `_resolution_source` before and after each test; verified the global is empty after the run.
