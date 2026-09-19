# Colibri Review - bug (DELTA) - PatternSkin/obs.py

- **Source path:** `PatternSkin/obs.py`
- **Reviewer:** claude-fable-5-1 (in-session), Colibri G37 protocol, campaign item 1 (product cores), rank 49
- **sha256 reviewed:** `34846e7566c8ac7abf20657da23c57fe1787633e9d237f0e497986290642604c` (sha8 `34846e75`)
- **Date:** 2026-09-10 · **Mode:** bug, stale-file DELTA against `e6d2f5c8` (2026-08-06 review)
- **Delta reviewed:** 5 commits / 191 diff lines: 60bbde28 + 83d109f8 (`timed_call` refuses generator/async functions), 53e12489 (GROK-OBS4 logging never raises into the timed path), f5562240 + a5911ef9 (PSK-SHADOW rotating field log + operator shadow with exact-arity wrappers) - every hunk read.
- **Context pack:** the prior review record(s) for the file, `docs/remediation_manifest.json` rows from 2026-07-24 on, `docs/deferred_manifest.json`, `_hunt_plan.json` + `_refuted_ledger.json` loaded; jCodemunch `get_symbol_source` on the symbols each finding depended on.

## Fixed since last review
- Every remediation row dated after the base review was verified present at the bytes (they are the delta).

## Verdict
Clean at the delta - the shadow wraps only a class's own invoke/execute with the exact arity bpy validates, marks each once, logs the traceback before re-raising; the file handler is replaced by name on reload, never stacked.

## Bugs & vulnerabilities
None confirmed at the delta.

---

# FULL re-audit 2026-09-10 (appended - the record above predates the adversarial gate and is kept as history, not as baseline)

# Colibri Review - bug (FULL re-audit) - PatternSkin/obs.py

- **Source path:** `PatternSkin/obs.py`
- **Reviewer:** claude-fable-5-1 (in-session fork), Colibri G37 protocol, campaign item 1 (product cores), rank 49
- **sha256 reviewed:** `34846e7566c8ac7abf20657da23c57fe1787633e9d237f0e497986290642604c` (sha8 `34846e75`)
- **Date:** 2026-09-10 · **Mode:** bug, FULL review of the current bytes (owner ruling 2026-09-10: the 08-06 review, GROK-OBS4, GLM-POLISH, PSK-SHADOW and this morning's delta are claims re-verified here)
- **Context pack:** all 205 lines read; importers `__init__.py:40` (register wires `attach_file_handler()` + `shadow_operators(_classes, _log)` at 8823-8824, unregister `detach_file_handler()` at 8878), `ai_parts.py:23`, `filmstrip.py:22`; a scan of every `_obs.`/`_log.`/`timed(` use inside `draw`/`poll`/`draw_header` bodies of the three importers (none), and of every logging call whose line mentions token/key/secret/bearer (none); dockets GROK-OBS4, GLM-POLISH; feature row PS-GLM-R2.

## Verdict
Clean. The file handler is bounded (1 MB x 3, delay=True), replaced by name on reload, released on unregister; the operator shadow wraps only a class's own invoke/execute with the exact arity bpy validates, marks each once, and logs a crash traceback before re-raising; every logging call in the module is guarded so a foreign handler can neither mask a failure nor destroy a paid result; no importer logs inside draw() and none logs a secret.

## Bugs & vulnerabilities
None confirmed.

## Missing safeguards (not fixed)
- `attach_file_handler` sets the `patternskin` logger to DEBUG and leaves `propagate=True`, so a host or foreign add-on that attaches a handler to the ROOT logger receives every Pattern Skin DEBUG record as well (duplicate console lines, never a failure).
- `log.exception` tracebacks carry source paths under the user's profile (the add-on's install path) - ordinary for a field log, worth remembering if the log is ever attached to a public bug report.

## Adversarial verification pass
- "`shadow_operators` after `register_class` would be ignored": bpy resolves `invoke`/`execute` by attribute lookup on the Python class at call time, and register() wraps BEFORE `register_class` anyway (8824 precedes the class loop) - refuted.
- "`_run` breaks an operator returning a non-set": the outcome formatting only joins when `r` is a set; anything else is logged with `%s` - refuted.
- "`timed_call` on a generator/coroutine logs 'ok' before the body runs": refused with `TypeError` at decoration (GLM-POLISH/GLM-R2) - verified present.
- "`detach_file_handler` leaves the file open across reloads": `h.close()` in a guarded try - refuted.
