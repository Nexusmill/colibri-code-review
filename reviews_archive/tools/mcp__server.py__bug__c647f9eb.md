# Colibri review — mcp/server.py (bug)

- **Source:** `C:\Users\User\source\repos\Tools\mcp\server.py`
- **Model:** claude-fable-5 (in-session), gating GLM-5.3-flash findings
- **sha256:** `c647f9eba880149cce51906118e877309215c8d32929a5bd91dfb939ff34516f` (GLM reviewed the same bytes)
- **Date:** 2026-09-02 · **Mode:** bug
- **Context:** stdlib stdio JSON-RPC MCP server exposing the six universal tools. Serial request loop.

## Verdict
One real HIGH (a valid-but-non-object JSON line crashes the whole server); the rest are robustness MEDIUM/LOW. Tool dispatch and the notification-suppression path are correct.

## Bugs & vulnerabilities

**[HIGH] A non-object JSON message crashes the server** — `handle()` line 197, `main()` line 224-232 — CONFIRMED (read)
- `json.loads` (line 229) accepts any valid JSON, including `[]`, `42`, `"x"`, `null`. `handle()` line 197 immediately does `msg.get("id")`; the only `try` wraps `run_tool` (208-211), not the dispatch, and `main()` calls `handle` unguarded. A non-dict message raises `AttributeError` out of `handle` → out of the loop → the stdio server dies mid-session; every later request fails until restart.
- Fix: in `main()` after `json.loads`, `if not isinstance(msg, dict): continue` (or reply `-32600 Invalid Request` with `id: None`).

**[MEDIUM] `screencap` success check trusts a pre-existing output file** — `run_tool` screencap branch — PLAUSIBLE (per GLM; not independently traced this pass)
- `ok = returncode==0 and os.path.exists(out)`: a stale file from a prior capture makes a failed/zero-byte capture read as success. Fix: capture start-time and require `getmtime(out) >= start` and/or `getsize(out) > 0`.

**[MEDIUM] `stdout.write`/`flush` unguarded against `BrokenPipeError`** — `main()` line 234-235 — CONFIRMED (read)
- If the host closes the pipe (common while a ≤20-min paid tool runs), the next write raises an unhandled traceback; and there is no cancellation path, so an in-flight paid `grok_review`/`hy4_review` keeps burning budget to its 1200s timeout. Fix: wrap write/flush in `try/except (BrokenPipeError, OSError): break`.

**[LOW] `initialize` echoes the client's `protocolVersion` unvalidated** — line 201 — CONFIRMED (read). Assert-compat with a version the server may not implement. Fix: return `PROTOCOL` unless the client's exactly matches.

## Missing safeguards
- `TimeoutExpired` on the paid tools surfaces as a bare error with no partial output; a clean "timed out, re-run at lower effort" result would help (LOW, per GLM).
