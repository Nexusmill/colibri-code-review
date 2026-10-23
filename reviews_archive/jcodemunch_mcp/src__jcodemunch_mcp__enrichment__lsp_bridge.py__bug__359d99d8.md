# Colibri review — src/jcodemunch_mcp/enrichment/lsp_bridge.py (bug)

- source: `C:\Users\User\source\repos\jcodemunch-mcp\src\jcodemunch_mcp\enrichment\lsp_bridge.py`
- model: claude-opus-5 (in-session Phase-3 gate over the 2026-09-11 sub-agent summary, artifacts reaudit/jcm/)
- sha256: `359d99d8175c1c9682f56f85e6c5fe04a01859b69f09d9df6b16e685a2fe6d62` (current bytes at dispatch, 2026-09-13; identical to the 2026-09-11 audit baseline)
- date: 2026-09-13
- mode: bug
- context pack: jCodemunch outline; `LSPServer` (lines 155-397: `start`/`stop`/`_send_request`/`_send_notification`/`_read_loop`/`_initialize`) and `_read_message` (119-148) and `LSPBridge._get_server` (426-461) read in full; the existing `tests/test_lsp_bridge.py` (40 tests, `subprocess` mocked — covers none of these, as the sub-agent noted and I confirmed by reading its fixtures); the five audit probes plus their fake stdio server re-run against these bytes (all RED); the sub-agent's sixth probe refuting the "project config can self-enable LSP" claim (ALL PASS, agreed). No prior `.colibri_reviews` record.

## Verdict
The bridge was fragile against any server that misbehaves even slightly — and real servers do all five of these things. Five defects, all reproduced against a real subprocess, all fixed in the commit carrying this record; the existing mocked suite stays green.

## Bugs & vulnerabilities
**[HIGH] `stderr=PIPE` is never drained — a chatty server blocks on its own write and every request times out — CONFIRMED — FIXED** - `line 192` (pre-fix numbering)
- Trigger: the server writes more than the pipe buffer (64 KB) to stderr — pyright's diagnostics logging does this routinely.
- Impact: the server hangs in `write(2)`; every in-flight and later request burns the full timeout; LSP enrichment silently yields nothing. Probe 1 (8 MB flood): `None` after the timeout.
- Fix: `_drain_stderr` daemon thread reads stderr to EOF and forwards lines to the debug log (kept, not DEVNULLed, so server diagnostics remain reachable).

**[HIGH] `_read_loop` exits on the first malformed frame and never fails its waiters — CONFIRMED — FIXED** - `line 119-148, 283-300` (pre-fix numbering)
- What: `_read_message` returned `None` for EOF AND for a stray blank line / missing Content-Length / undecodable body, and the loop `break`s on `None`. After one odd frame the process stays "running" with no reader — every later request times out for the rest of the session. Separately, when the server EXITS the loop broke without waking pending events, so a caller waited the full timeout for a process that was already gone (probe 2 "die": 2.00 s vs a 2 s timeout).
- Fix: `None` now means EOF only; malformed frames are skipped and come back as `{}` (a stray leading blank line is consumed before the headers, a non-dict body is discarded). On loop exit every pending event is set with a `None` response so waiters fail promptly. The loop reads to EOF rather than polling `is_running` — EOF is the authoritative "gone" signal.

**[HIGH] Server-initiated requests misrouted as responses — CONFIRMED — FIXED** - `line 290-296` (pre-fix numbering)
- What: a message carrying `method` AND `id` (`workspace/configuration`, `client/registerCapability`, `window/workDoneProgress/create` — all routine) is a request in the SERVER's id space; when its id collided with a pending client id the bridge popped our event, stored `result=None`, and the real response was later dropped as unknown. Probe 3: definition answered `None`, and the server's request never got a reply (`uri=file:///missing`).
- Fix: any message with `method` is routed as server→client traffic and never touches `_pending`; requests are declined with JSON-RPC `-32601` so the server does not block waiting. A `_write_lock` serialises stdin now that two threads write it.

**[HIGH] Windows: `.cmd` shims found by `which()` but launched by bare name — CONFIRMED — FIXED** - `line 449-455` (pre-fix numbering)
- What: `shutil.which("pyright-langserver")` finds the npm `pyright-langserver.cmd` via PATHEXT; `Popen(["pyright-langserver", ...])` (no shell) asks CreateProcess for the bare name, which does not apply PATHEXT → `FileNotFoundError` → the language is marked failed. Probe 4 on this Windows box: `[WinError 2]`.
- Impact: LSP enrichment for Python and TypeScript/JavaScript — the two most common integrations — never works on Windows via a standard npm global install.
- Fix: launch `[resolved, *command[1:]]` — the path `which()` actually found.

**[MEDIUM] `stop()` runs the shutdown handshake against a server that never initialized — CONFIRMED — FIXED** - `line 222-227` (pre-fix numbering)
- A failed `initialize` (timeout) was followed by `_send_request("shutdown")` — another full timeout — before `terminate()`. Probe 5: 2.03 s teardown at a 1 s timeout. Fix: the graceful handshake runs only when `_initialized`.

## Refuted (sub-agent's own, re-checked and agreed)
- "An indexed repo's `.jcodemunch.jsonc` can self-enable LSP and pick the binary" — with the global layer silent, project `lsp_enabled=true` has no effect (probe 6 ALL PASS on these bytes; `is_lsp_enabled` reads the global key).

## Adversarial verification (Phase 3)
- Every defect was reproduced against a REAL child process (the fake stdio server in `tests/_fake_lsp_server.py`, one misbehaviour per mode) rather than a mock, then re-verified GREEN with the same harness — the mocked suite could not have seen any of them.
- Checked that reading to EOF instead of polling `is_running` cannot leak the thread: daemon thread; `stop()` closes the process so stdout hits EOF.
- Checked that declining server requests with `-32601` is safe for the two servers shipped in `DEFAULT_LSP_SERVERS`: both treat a `workspace/configuration` error as "use defaults" (JSON-RPC error responses are a defined outcome, not a protocol violation).
- Ran the new battery three times back-to-back (47/47 each) to rule out timing flakes; the one race I found was in MY test (poll() lagging EOF by a beat) and was fixed in the test, not papered over in the code.

## Remediation postscript (same commit)
The fixes were applied after this review hashed the bytes above; the file is now `75818af9e989ca634b9243f10ae7babcb53eb665a39c4bef9cc89500a4566de8`. TDD: `tests/test_lsp_bridge_process.py` (7 tests, real subprocess) all RED on the old bytes for exactly the stated defects, GREEN after; `tests/test_lsp_bridge.py` 40/40 unchanged; enrichment suites 66 green.
